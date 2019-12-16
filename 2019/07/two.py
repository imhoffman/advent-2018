#!/usr/bin/env python3

from math import factorial
from itertools import permutations

##
##  subprograms
##

#  unpack individual integers from compound Intcode
def parse_opcode ( ABCDE ):
    A, B, C = 0, 0, 0
    as_char_array = str( ABCDE )
    opcode = int( as_char_array[-1:] )
    if opcode == 9 and len(as_char_array) > 1 and int( as_char_array[-2:-1] ) == 9:
        opcode = 99
    if as_char_array[-3:-2]:
        C = int( as_char_array[-3:-2] )
    if as_char_array[-4:-3]:
        B = int( as_char_array[-4:-3] )
    if as_char_array[-5:-4]:
        A = int( as_char_array[-5:-4] )
    return opcode, (C, B, A)

#  for fetching the appropriate value as per the instruction modalities
#   "Parameters that an instruction writes to will never be in immediate mode."
def modal_parameters ( opcode, ram, ip, modes, base ):
    if opcode == 99:
        return 0, 0, 0
    # first param; arg1 is the writing location of opcode 3
    if opcode == 3:
        if modes[0] == 2:
            arg1 = ram[ip+1] + base
        else:
            arg1 = ram[ip+1]
    else:
        if modes[0] == 1:
            arg1 = ram[ip+1]
        elif modes[0] == 2:
            arg1 = ram[ ram[ip+1] + base ]
        else:
            arg1 = ram[ ram[ip+1] ]
    # second param
    if modes[1] == 1:
        arg2 = ram[ip+2]
    elif modes[1] == 2:
        arg2 = ram[ ram[ip+2] + base ]
    else:
        arg2 = ram[ ram[ip+2] ]
    # third param; arg3 is the writing location of opcodes 1,2,7,8
    if modes[2] == 2:
        arg3 = ram[ip+3] + base
    else:
        arg3 = ram[ip+3]
    return arg1, arg2, arg3



class Amplifier(object):
    def __init__( self, program, phase_setting ):
        self.ram = program
        self.base_addr = 0
        self.input_value = phase_setting
        self.phase_not_yet_set = True
        self.original_program = []
        self.original_program[:] = program[:]
        self.ip = 0
        return


    def input_to_program ( self, new_input ):
        if self.phase_not_yet_set:
            self.phase_not_yet_set = False
        else:
            self.input_value = new_input
        return


    def output_from_program ( self, value ):
        return value
            

    def processor ( self ):
        ram = self.ram
        ip = self.ip
        base_addr = self.base_addr
        opcode, modes = parse_opcode( ram[ip] )
        arg1, arg2, arg3 = modal_parameters( opcode, ram, ip, modes, base_addr )
        output_value = -5
        if   opcode == 1:
            ram[ arg3 ] = arg1 + arg2
            return ram, ip+4, base_addr, output_value
        elif opcode == 2:
            ram[ arg3 ] = arg1 * arg2
            return ram, ip+4, base_addr, output_value
        elif opcode == 3:
            input_value = self.input_value
            if input_value < 0:
                output_value = -3   # this means `still running, waiting for input`
                return ram, ip, base_addr, output_value    # hold on input ip
            else:
                ram[ arg1 ] = input_value
                output_value = -4   # a neg value other than -3 ??
            return ram, ip+2, base_addr, output_value
        elif opcode == 4:
            output_value = arg1
            return ram, ip+2, base_addr, output_value
        elif opcode == 5:
            if arg1:
                return ram, arg2, base_addr, output_value
            else:
                return ram, ip+3, base_addr, output_value
        elif opcode == 6:
            if not arg1:
                return ram, arg2, base_addr, output_value
            else:
                return ram, ip+3, base_addr, output_value
        elif opcode == 7:
            if arg1 < arg2:
                ram[ arg3 ] = 1
            else:
                ram[ arg3 ] = 0
            return ram, ip+4, base_addr, output_value
        elif opcode == 8:
            if arg1 == arg2:
                ram[ arg3 ] = 1
            else:
                ram[ arg3 ] = 0
            return ram, ip+4, base_addr, output_value
        elif opcode == 9:
            return ram, ip+2, base_addr + arg1, output_value
        elif opcode == 99:
            output_value = -1
            return ram, -1, base_addr, output_value
        else:
            print("unknown opcode")
        return


    def generate_output( self ):
        output_value = 0
        good_output_value = -888
        while output_value not in (-1,-3):  # halted or needs to wait for input
            self.program, self.ip, self.base_addr, output_value = \
                    self.processor()
        if output_value >= 0:   # keep any good output, then continue program
            good_output_value = output_value
        if output_value == -1:
            good_output_value = -999   # some irrelevant value; we're hatling
        if good_output_value == -888 and output_value == -3:
            print( "\n attemping to enter wait mode without having outputed!" )
        return good_output_value, output_value
##  end of Amplifier class




def thrusters( program, phase_settings ):
    # "memory is not shared or reused between copies of the program"
    Amp_A = Amplifier( program, phase_settings[0] )
    Amp_B = Amplifier( program, phase_settings[1] )
    Amp_C = Amplifier( program, phase_settings[2] )
    Amp_D = Amplifier( program, phase_settings[3] )
    Amp_E = Amplifier( program, phase_settings[4] )
    amps = [ Amp_A, Amp_B, Amp_C, Amp_D, Amp_E ]

    for amp in amps:
        amp.input_to_program(0)      # initialize phase setting
    Amp_A.input_to_program(0)        # start to process with a 0 to A
    while True:
        Amp_B.input_to_program( Amp_A.generate_output()[0] )
        Amp_C.input_to_program( Amp_B.generate_output()[0] )
        Amp_D.input_to_program( Amp_C.generate_output()[0] )
        Amp_E.input_to_program( Amp_D.generate_output()[0] )
        inp_A, exit_code = Amp_E.generate_output()
        if exit_code == -1:    # if E halts (-1 rather than -3), we're done
            break
        print( " Amp A just received %d from Amp E\n" % inp_A )
        Amp_A.input_to_program( inp_A )

    return inp_A


#  https://docs.python.org/3.8/library/itertools.html#itertools.permutations
def search_phase_settings( program ):
    temp_max = 0
    for p in ( (9,7,8,5,6), (5,6,7,8,9) ):
    #for p in permutations( (9,8,7,6,5) ):
        trial = thrusters( program, p )
        if trial > temp_max:
            temp_max = trial
            best_config = p
    return temp_max, best_config



##
##  main program
##
with open("puzzle.txt") as fo:
  line = fo.readline()

program = [ int( s ) for s in line.rstrip().split(sep=",") ]

print( "\n read %d commands from input file\n" % ( len(program) ) )

answer, config = search_phase_settings( program ) 
print( "\n For phases", config, "maximal thruster output", answer, "is obtained.\n\n" )

