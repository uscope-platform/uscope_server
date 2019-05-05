#include <sys/types.h>
#include <sys/stat.h>
#include <sys/mman.h>

#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <stdio.h>


uint32_t fd_data;
int mmap_fd1;
int mmap_fd2;

uint32_t mmap_size;

volatile uint32_t* buffer;
volatile uint32_t* dma_controls;
volatile uint32_t* registers;



#define FATAL do { fprintf(stderr, "Error at line %d, file %s (%d) [%s]\n", \
  __LINE__, __FILE__, errno, strerror(errno)); exit(1); } while(0)

int low_level_init(char* filename, int size, int dma_addr, int reg_addr){


    //mmap buffer
    fd_data = open(filename, O_RDWR| O_SYNC);
    mmap_size = size;

    buffer = (uint32_t* ) mmap(NULL, mmap_size, PROT_READ, MAP_SHARED, fd_data, 0);
    if(buffer < 0) {
      fprintf(stderr, "Cannot mmap uio device: %s\n",
        strerror(errno));
    }

    if((mmap_fd2 = open("/dev/mem", O_RDWR | O_SYNC)) == -1) FATAL;
    dma_controls = (uint32_t* ) mmap(0, 11*sizeof(uint32_t),  PROT_READ | PROT_WRITE, MAP_SHARED, mmap_fd2, dma_addr);
    if(dma_controls < 0) {
      fprintf(stderr, "Cannot mmap dma controls: %s\n",
        strerror(errno));
    }

    if((mmap_fd1 = open("/dev/mem", O_RDWR | O_SYNC)) == -1) FATAL;

    registers = (uint32_t* ) mmap(0, 6*4096,  PROT_READ | PROT_WRITE, MAP_SHARED, mmap_fd1, reg_addr);

    //Configure SPI peripheral
    registers[1] = 0x28;
    registers[0] = 0x5C4;

    //Configure Adc processing chain
    registers[68] = 0x0B04051B;
    registers[69] = 0x146D1086;
    registers[70] = 0x146D15D6;
    registers[71] = 0x0B041086;
    registers[72] = 0x051B;
    registers[73] = 0x0;
    registers[74] = 0x1;
    return(fd_data);
}


int wait_for_Interrupt(void){
    uint32_t read_val;
    int ret_val = read(fd_data, &read_val, sizeof(read_val));
    dma_controls[6] = 0xC0000000;
    dma_controls[8] = 0x100000;
    dma_controls[10] = 0x1000;

    if(ret_val < 0) {
      fprintf(stderr, "Cannot wait for uio device interrupt: %s\n",
        strerror(errno));
    }
    return ret_val;
}

int acknowledge_interrupt(void){
    uint32_t write_val = 1;
    int ret_val = write(fd_data, &write_val, sizeof(write_val));

     if(ret_val<0) {
      fprintf(stderr, "Cannot acknowledge uio device interrupt: %s\n",
        strerror(errno));
    }

    return ret_val;
}

void read_data(uint32_t *data){
    memcpy(data, buffer,20*sizeof(uint32_t));
}