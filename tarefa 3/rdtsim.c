#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BIDIRECTIONAL 0
                       

struct msg {
    char data[20];
};

struct pkt {
    int seqnum;
    int acknum;
    int checksum;
    char payload[20];
};

void starttimer(int AorB, float increment);
void stoptimer(int AorB);
void tolayer3(int AorB, struct pkt packet);
void tolayer5(int AorB, char datasent[20]);

enum SenderState {
    WAIT_LAYER5,
    WAIT_ACK
};

struct Sender {
    enum SenderState state;
    int seq;
    float estimated_rtt;
    struct pkt last_packet;
} A;

struct Receiver {
    int seq;
} B;

int get_checksum(struct pkt *packet) {
    int checksum = 0;
    checksum += packet->seqnum;
    checksum += packet->acknum;
    for (int i = 0; i < 20; ++i)
        checksum += packet->payload[i];
    return checksum;
}

void A_output(struct msg message) {
    if (A.state != WAIT_LAYER5) {
        printf("  A_output: not yet acked. drop the message: %s\n", message.data);
        return;
    }
    printf("  A_output: send packet: %s\n", message.data);
    struct pkt packet;
    packet.seqnum = A.seq;
    memmove(packet.payload, message.data, 20);
    packet.checksum = get_checksum(&packet);
    A.last_packet = packet;
    A.state = WAIT_ACK;
    tolayer3(0, packet);
    starttimer(0, A.estimated_rtt);
}

void B_output(struct msg message) {
    printf("  B_output: uni-directional. ignore.\n");
}

void A_input(struct pkt packet) {
    if (A.state != WAIT_ACK) {
        printf("  A_input: A->B only. drop.\n");
        return;
    }
    if (packet.checksum != get_checksum(&packet)) {
        printf("  A_input: packet corrupted. drop.\n");
        return;
    }

    if (packet.acknum != A.seq) {
        printf("  A_input: not the expected ACK. drop.\n");
        return;
    }
    printf("  A_input: acked.\n");
    stoptimer(0);
    A.seq = 1 - A.seq;
    A.state = WAIT_LAYER5;
}

void A_timerinterrupt(void) {
    if (A.state != WAIT_ACK) {
        printf("  A_timerinterrupt: not waiting ACK. ignore event.\n");
        return;
    }
    printf("  A_timerinterrupt: resend last packet: %s.\n", A.last_packet.payload);
    tolayer3(0, A.last_packet);
    starttimer(0, A.estimated_rtt);
}

void A_init(void) {
    A.state = WAIT_LAYER5;
    A.seq = 0;
    A.estimated_rtt = 15;
}

void send_ack(int AorB, int ack) {
    struct pkt packet;
    packet.acknum = ack;
    packet.checksum = get_checksum(&packet);
    tolayer3(AorB, packet);
}

void B_input(struct pkt packet) {
    if (packet.checksum != get_checksum(&packet)) {
        printf("  B_input: packet corrupted. send NAK.\n");
        send_ack(1, 1 - B.seq);
        return;
    }
    if (packet.seqnum != B.seq) {
        printf("  B_input: not the expected seq. send NAK.\n");
        send_ack(1, 1 - B.seq);
        return;
    }
    printf("  B_input: recv message: %s\n", packet.payload);
    printf("  B_input: send ACK.\n");
    send_ack(1, B.seq);
    tolayer5(1, packet.payload);
    B.seq = 1 - B.seq;
}

void B_timerinterrupt(void) {
    printf("  B_timerinterrupt: B doesn't have a timer. ignore.\n");
}

void B_init(void) {
    B.seq = 0;
}

struct event {
    float evtime;      
    int evtype;        
    int eventity;      
    struct pkt *pktptr;
    struct event *prev;
    struct event *next;
};
struct event *evlist = NULL;

/* possible events: */
#define TIMER_INTERRUPT 0
#define FROM_LAYER5 1
#define FROM_LAYER3 2

#define OFF 0
#define ON 1
#define A 0
#define B 1

int TRACE = 1;    
int nsim = 0;     
int nsimmax = 0;  
float time = 0.000;
float lossprob;   
float corruptprob;
float lambda;     
int ntolayer3;    
int nlost;        
int ncorrupt;     

void init(int argc, char **argv);
void generate_next_arrival(void);
void insertevent(struct event *p);

int main(int argc, char **argv) {
    struct event *eventptr;
    struct msg msg2give;
    struct pkt pkt2give;

    int i, j;
    char c;

    init(argc, argv);
    A_init();
    B_init();

    while (1) {
        eventptr = evlist;
        if (eventptr == NULL)
            goto terminate;
        evlist = evlist->next;
        if (evlist != NULL)
            evlist->prev = NULL;
        if (TRACE >= 2) {
            printf("\nEVENT time: %f,", eventptr->evtime);
            printf("  type: %d", eventptr->evtype);
            if (eventptr->evtype == 0)
                printf(", timerinterrupt  ");
            else if (eventptr->evtype == 1)
                printf(", fromlayer5 ");
            else
                printf(", fromlayer3 ");
            printf(" entity: %d\n", eventptr->eventity);
        }
        time = eventptr->evtime;
        if (eventptr->evtype == FROM_LAYER5) {
            if (nsim < nsimmax) {
                if (nsim + 1 < nsimmax)
                    generate_next_arrival();
               
                j = nsim % 26;
                for (i = 0; i < 20; i++)
                    msg2give.data[i] = 97 + j;
                msg2give.data[19] = 0;
                if (TRACE > 2) {
                    printf("          MAINLOOP: data given to student: ");
                    for (i = 0; i < 20; i++)
                        printf("%c", msg2give.data[i]);
                    printf("\n");
                }
                nsim++;
                if (eventptr->eventity == A)
                    A_output(msg2give);
                else
                    B_output(msg2give);
            }
        } else if (eventptr->evtype == FROM_LAYER3) {
            pkt2give.seqnum = eventptr->pktptr->seqnum;
            pkt2give.acknum = eventptr->pktptr->acknum;
            pkt2give.checksum = eventptr->pktptr->checksum;
            for (i = 0; i < 20; i++)
                pkt2give.payload[i] = eventptr->pktptr->payload[i];
            if (eventptr->eventity == A)
                A_input(pkt2give);
            else
                B_input(pkt2give);
            free(eventptr->pktptr);
        } else if (eventptr->evtype == TIMER_INTERRUPT) {
            if (eventptr->eventity == A)
                A_timerinterrupt();
            else
                B_timerinterrupt();
        } else {
            printf("INTERNAL PANIC: unknown event type \n");
        }
        free(eventptr);
    }

terminate:
    printf(
            " Simulator terminated at time %f\n after sending %d msgs from layer5\n",
            time, nsim);
}

void init(int argc, char **argv)
{
    int i;
    float sum, avg;
    float jimsrand();

    if (argc != 6) {
        printf("usage: %s  num_sim  prob_loss  prob_corrupt  interval  debug_level\n", argv[0]);
        exit(1);
    }

    nsimmax = atoi(argv[1]);
    lossprob = atof(argv[2]);
    corruptprob = atof(argv[3]);
    lambda = atof(argv[4]);
    TRACE = atoi(argv[5]);
    printf("-----  Stop and Wait Network Simulator Version 1.1 -------- \n\n");
    printf("the number of messages to simulate: %d\n", nsimmax);
    printf("packet loss probability: %f\n", lossprob);
    printf("packet corruption probability: %f\n", corruptprob);
    printf("average time between messages from sender's layer5: %f\n", lambda);
    printf("TRACE: %d\n", TRACE);


    srand(9999);
    sum = 0.0;  
    for (i = 0; i < 1000; i++)
        sum = sum + jimsrand();
    avg = sum / 1000.0;
    if (avg < 0.25 || avg > 0.75) {
        printf("It is likely that random number generation on your machine\n");
        printf("is different from what this emulator expects.  Please take\n");
        printf("a look at the routine jimsrand() in the emulator code. Sorry. \n");
        exit(1);
    }

    ntolayer3 = 0;
    nlost = 0;
    ncorrupt = 0;

    time = 0.0;             
    generate_next_arrival();
}

float jimsrand(void) {
    double mmm = RAND_MAX;
    float x;                
    x = rand() / mmm;       
    return (x);
}

void generate_next_arrival(void) {
    double x, log(), ceil();
    struct event *evptr;
    float ttime;
    int tempint;

    if (TRACE > 2)
        printf("          GENERATE NEXT ARRIVAL: creating new arrival\n");

    x = lambda * jimsrand() * 2;
                                                            
    evptr = (struct event *)malloc(sizeof(struct event));
    evptr->evtime = time + x;
    evptr->evtype = FROM_LAYER5;
    if (BIDIRECTIONAL && (jimsrand() > 0.5))
        evptr->eventity = B;
    else
        evptr->eventity = A;
    insertevent(evptr);
}

void insertevent(struct event *p) {
    struct event *q, *qold;

    if (TRACE > 2) {
        printf("            INSERTEVENT: time is %lf\n", time);
        printf("            INSERTEVENT: future time will be %lf\n", p->evtime);
    }
    q = evlist;     
    if (q == NULL) {
        evlist = p;
        p->next = NULL;
        p->prev = NULL;
    } else {
        for (qold = q; q != NULL && p->evtime > q->evtime; q = q->next)
            qold = q;
        if (q == NULL) {
            qold->next = p;
            p->prev = qold;
            p->next = NULL;
        } else if (q == evlist) {
            p->next = evlist;
            p->prev = NULL;
            p->next->prev = p;
            evlist = p;
        } else {
            p->next = q;
            p->prev = q->prev;
            q->prev->next = p;
            q->prev = p;
        }
    }
}

void printevlist(void) {
    struct event *q;
    int i;
    printf("--------------\nEvent List Follows:\n");
    for (q = evlist; q != NULL; q = q->next) {
        printf("Event time: %f, type: %d entity: %d\n", q->evtime, q->evtype,
                     q->eventity);
    }
    printf("--------------\n");
}

void stoptimer(int AorB) {
    struct event *q, *qold;

    if (TRACE > 2)
        printf("          STOP TIMER: stopping timer at %f\n", time);
   
    for (q = evlist; q != NULL; q = q->next)
        if ((q->evtype == TIMER_INTERRUPT && q->eventity == AorB)) {
           
            if (q->next == NULL && q->prev == NULL)
                evlist = NULL;         
            else if (q->next == NULL)
                q->prev->next = NULL;
            else if (q == evlist) {
                q->next->prev = NULL;
                evlist = q->next;
            } else {
                q->next->prev = q->prev;
                q->prev->next = q->next;
            }
            free(q);
            return;
        }
    printf("Warning: unable to cancel your timer. It wasn't running.\n");
}

void starttimer(int AorB , float increment) {
    struct event *q;
    struct event *evptr;

    if (TRACE > 2)
        printf("          START TIMER: starting timer at %f\n", time);
   
   
    for (q = evlist; q != NULL; q = q->next)
        if ((q->evtype == TIMER_INTERRUPT && q->eventity == AorB)) {
            printf("Warning: attempt to start a timer that is already started\n");
            return;
        }

   
    evptr = (struct event *)malloc(sizeof(struct event));
    evptr->evtime = time + increment;
    evptr->evtype = TIMER_INTERRUPT;
    evptr->eventity = AorB;
    insertevent(evptr);
}

void tolayer3(int AorB , struct pkt packet) {
    struct pkt *mypktptr;
    struct event *evptr, *q;
    float lastime, x;
    int i;

    ntolayer3++;

    if (jimsrand() < lossprob) {
        nlost++;
        if (TRACE > 0)
            printf("          TOLAYER3: packet being lost\n");
        return;
    }

    mypktptr = (struct pkt *)malloc(sizeof(struct pkt));
    mypktptr->seqnum = packet.seqnum;
    mypktptr->acknum = packet.acknum;
    mypktptr->checksum = packet.checksum;
    for (i = 0; i < 20; i++)
        mypktptr->payload[i] = packet.payload[i];
    if (TRACE > 2) {
        printf("          TOLAYER3: seq: %d, ack %d, check: %d ", mypktptr->seqnum,
                     mypktptr->acknum, mypktptr->checksum);
        for (i = 0; i < 20; i++)
            printf("%c", mypktptr->payload[i]);
        printf("\n");
    }

    evptr = (struct event *)malloc(sizeof(struct event));
    evptr->evtype = FROM_LAYER3;     
    evptr->eventity = (AorB + 1) % 2;
    evptr->pktptr = mypktptr;        
                                     
    lastime = time;
   
    for (q = evlist; q != NULL; q = q->next)
        if ((q->evtype == FROM_LAYER3 && q->eventity == evptr->eventity))
            lastime = q->evtime;
    evptr->evtime = lastime + 1 + 9 * jimsrand();

   
    if (jimsrand() < corruptprob) {
        ncorrupt++;
        if ((x = jimsrand()) < .75)
            mypktptr->payload[0] = 'Z';
        else if (x < .875)
            mypktptr->seqnum = 999999;
        else
            mypktptr->acknum = 999999;
        if (TRACE > 0)
            printf("          TOLAYER3: packet being corrupted\n");
    }

    if (TRACE > 2)
        printf("          TOLAYER3: scheduling arrival on other side\n");
    insertevent(evptr);
}

void tolayer5(int AorB, char datasent[20]) {
    int i;
    if (TRACE > 2) {
        printf("          TOLAYER5: data received: ");
        for (i = 0; i < 20; i++)
            printf("%c", datasent[i]);
        printf("\n");
    }
}
