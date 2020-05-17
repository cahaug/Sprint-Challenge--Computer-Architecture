"""CPU functionality."""

import sys

# OP CODES
HLT = 0b00000001   # Halt function, if HLT is encountered running = False
LDI = 0b10000010   # SAVE function
PRN = 0b01000111   # PRINT function
MUL = 0b10100010   # MULTIPLY function
PUSH = 0b01000101  # PUSH function -- add the value from the given register to the stack
POP = 0b01000110   # POP function -- pop the value from the top of the stack to the given register
CALL = 0b01010000  # CALL function
RET = 0b00010001   # RET function
ADD = 0b10100000   # ADD function
CMP = 0b10100111   # CMP - compare, ALU function, compares two values and set appropriate Equals flag

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.SP = 7
        self.reg[self.SP] = len(self.ram) - 12 #initiate stack at F4 per readme
        self.running = False
        self.branchtable = {}
        self.branchtable[HLT] = self.handle_halt
        self.branchtable[LDI] = self.handle_save
        self.branchtable[PRN] = self.handle_print
        self.branchtable[MUL] = self.handle_mul
        self.branchtable[PUSH] = self.handle_push
        self.branchtable[POP] = self.handle_pop
        self.branchtable[CALL] = self.handle_call
        self.branchtable[RET] = self.handle_ret
        self.branchtable[ADD] = self.handle_add
        self.branchtable[CMP] = self.handle_cmp
        
    def load(self):
        """Load a program into memory."""
        address = 0
        arguments = sys.argv
        if len(arguments) < 2:
            print('Need proper filename passed')
            sys.exit(1)
        filename = arguments[1]
        with open(filename) as f:
            for line in f:
                comment_split = line.split('#')
                if comment_split[0] == '' or comment_split[0] == '\n':
                    continue
                command = comment_split[0].strip()
                # print(command, int(command, 2))
                self.ram_write(int(command, 2), address)
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
        # elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, MAR):
        return(self.ram[MAR])

    def ram_write(self, MDR, MAR):
        # print(MDR, MAR)
        self.ram[MAR] = MDR

    def handle_halt(self):
        self.running = False
        self.pc += 1

    def handle_save(self):
        # get the value to be saved from ram
        val_to_save = self.ram[self.pc + 2]
        # get destination from ram
        destination = self.ram[self.pc + 1]
        # save_to_ram
        self.reg[destination] = val_to_save
        # increment pc
        self.pc += 3

    def handle_mul(self):
        self.alu('MUL', self.ram[self.pc + 1], self.ram[self.pc + 2])
        self.pc += 3

    def handle_add(self):
        self.alu('ADD', self.ram[self.pc + 1], self.ram[self.pc + 2])
        self.pc += 3

    def handle_print(self):
        # get reg location of value to print
        reg_loc = self.ram[self.pc + 1]
        # get value to print
        val_to_print = self.reg[reg_loc]
        # print it
        print(f'Requested Value: {val_to_print}')
        # increment pc
        self.pc += 2

    def handle_push(self):
        # load register from ram
        reg = self.ram[self.pc + 1]
        # decrement stack pointer
        self.reg[self.SP] -= 1
        #prep for push
        reg_value = self.reg[reg]
        #save to ram
        self.ram[self.reg[self.SP]] = reg_value
        #increment program counter
        self.pc += 2

    def handle_pop(self):
        value = self.ram[self.reg[self.SP]]
        # load register from ram
        reg = self.ram[self.pc + 1]
        self.reg[reg] = value
        self.reg[self.SP] += 1
        self.pc += 2

    def handle_call(self):
        self.reg[self.SP] -= 1
        self.ram[self.reg[self.SP]] = self.pc + 2
        reg = self.ram[self.pc + 1]
        reg_value = self.reg[reg]
        self.pc = reg_value

    def handle_ret(self):
        # read value from memory
        return_value = self.ram[self.reg[self.SP]]
        # increment the stack pointer
        self.reg[self.SP] += 1
        # send the value to the program counter
        self.pc = return_value

    def handle_cmp(self):
        pass


    def run(self):
        """Run the CPU."""
        IR = None
        # inst_inc = 0
        self.running = True

        while self.running:
            # self.trace()
            # Add our instruction to the instruction register from ram
            IR = self.ram[self.pc]
            # Extract the command
            COMMAND = IR
            # print(COMMAND)

            # Execution Loop #
            if COMMAND in self.branchtable:
                self.branchtable[COMMAND]()
            else:
                # error message
                print(f'Unknown instruction, {COMMAND}')
                # crash
                sys.exit(1)

