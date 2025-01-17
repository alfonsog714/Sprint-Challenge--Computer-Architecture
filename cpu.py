"""CPU functionality."""

import sys

# HALT = 1
# SAVE = 130
# PRINT = 71


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.ram = [0] * 256  # 256 or 2048?
        self.registers = [0] * 8
        self.instructions = {
            'HALT': 0b00000001,
            'LDI': 0b10000010,
            'PRN': 0b01000111,
            'MUL': 0b10100010,
            'JMP': 0b01010100,
            'CMP': 0b10100111,
            'JEQ': 0b01010101,
            'JNE': 0b01010110
        }

        # Specific registers
        # 0 1 2 3 4 5 6 7
        #            < > =
        self.flag = [0] * 8

    def load(self):
        """Load a program into memory."""

        address = 0

        if len(sys.argv) != 2:
            print("Usage: file.py <filename>", file=sys.stderr)
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                for line in f:

                    # Ignore anything after a #
                    comment_split = line.split("#")

                    # Convert any numbers from binary strings to integers
                    num = comment_split[0].strip()

                    try:
                        # int takes a 2nd argument that is the base to use. we use 2 because binary counts using a base of 2
                        x = int(num, 2)
                        self.ram_write(x, address)
                        address += 1

                    except ValueError:
                        continue

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} not found.")
            sys.exit(2)

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value
        return self.ram[address]

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.registers[reg_a] += self.registers[reg_b]

        elif op == 'MUL':
            self.registers[reg_a] *= self.registers[reg_b]

        elif op == "SUB":
            self.registers[reg_a] -= self.registers[reg_b]

        elif op == "CMP":
            self.flag[5] = 0
            self.flag[6] = 0
            self.flag[7] = 0

            if reg_a == reg_b:
                self.flag[7] = 1

            elif reg_a > reg_b:
                self.flag[6] = 1

            # elif reg_a < reg_b:
            #     self.flag[5] = 1

            else:
                self.flag[5] = 1

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
            print(" %02X" % self.registers[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        running = True

        while running:
            command = self.ram[self.pc]

            if command == self.instructions['HALT']:
                running = False
                self.pc += 1

            elif command == self.instructions['LDI']:
                # self.trace()
                reg = self.ram[self.pc + 1]
                value = self.ram[self.pc + 2]
                self.registers[reg] = value
                self.pc += 3

            elif command == self.instructions['PRN']:
                # self.trace()
                reg = self.ram[self.pc + 1]
                print(self.registers[reg])
                self.pc += 2

            elif command == self.instructions['MUL']:
                # self.trace()
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]
                self.alu('MUL', reg_a, reg_b)
                self.pc += 3

            elif command == self.instructions['CMP']:
                # self.trace()
                reg_a = self.registers[self.ram[self.pc + 1]]
                reg_b = self.registers[self.ram[self.pc + 2]]
                self.alu('CMP', reg_a, reg_b)
                self.pc += 3

            elif command == self.instructions['JMP']:
                # self.trace()
                # print(reg)
                self.pc = self.registers[self.ram[self.pc + 1]]

            elif command == self.instructions['JEQ']:

                if self.flag[7] == 1:
                    self.pc = self.registers[self.ram[self.pc + 1]]
                else:
                    # print(f"{reg} - Flag is not equal")
                    self.pc += 2

            elif command == self.instructions['JNE']:

                if self.flag[7] == 0:
                    self.pc = self.registers[self.ram[self.pc + 1]]
                else:
                    # print(f"{reg} - Flag is not equal")
                    self.pc += 2
            else:
                # self.trace()
                print(f"Unkown instruction: {bin(command)} - {command}")
                sys.exit(1)
