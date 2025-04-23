#include <stdio.h>
#include <sys/wait.h> 
#include <unistd.h>

#define ITER_MAX 1000
#define SLEEP 1.0
// #define SLEEP 10

int main(void)
{
   char msg_p[] = "parent";
   char msg_c[] = "child";
   char nl[] = "\n";
   int i; 

   for (i=0; i<ITER_MAX; i++){
      if (fork()) {
         sleep(SLEEP); 
        //  printf("parent"); fflush(stdout); 
         write(STDOUT_FILENO, msg_p, sizeof(nl)-1);
         wait(NULL);
     } else {
         sleep(SLEEP); 
        //  printf("child"); fflush(stdout);
         write(STDOUT_FILENO, msg_c, sizeof(nl)-1);
         return 0;
     }
     sleep(SLEEP);
    //  printf("\n"); fflush(stdout);
     write(STDOUT_FILENO, nl, sizeof(nl)-1);
 }

 return 0;
}