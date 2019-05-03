#include <sys/types.h>
#include <sys/stat.h>
#include <sys/mman.h>

#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <stdio.h>


uint32_t fd;
uint32_t mmap_size;
volatile uint32_t* buffer;

int low_level_init(char* filename, int size){

    fd = open(filename, O_RDWR);
    mmap_size = size;
    buffer = (uint32_t* )mmap(NULL, mmap_size, PROT_READ, MAP_SHARED, fd, 0);
    if(buffer < 0)
    {
      fprintf(stderr, "Cannot mmap uio device: %s\n",
        strerror(errno));
    }

    return(fd);
}

int wait_for_Interrupt(void){
    uint32_t read_val;
    int ret_val = read(fd, &read_val, sizeof(read_val));

    if(ret_val < 0)
    {
      fprintf(stderr, "Cannot wait for uio device interrupt: %s\n",
        strerror(errno));
    }
    return ret_val;
}

int acknowledge_interrupt(void){
    uint32_t write_val = 1;
    int ret_val = write(fd, &write_val, sizeof(write_val));

     if(ret_val<0) {
      fprintf(stderr, "Cannot acknowledge uio device interrupt: %s\n",
        strerror(errno));
    }

    return ret_val;
}

void read_data(uint32_t *data){
    memcpy(data, buffer,20*sizeof(uint32_t));
}