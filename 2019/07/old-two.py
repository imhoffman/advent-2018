#!/usr/bin/env python3

from math import factorial
from itertools import permutations

##
##  subprograms
##

def parse_opcode ( ABCDE ):
    as_char_array = str( ABCDE )
    opcode = int( as_char_array[-1:] )
    if opcode == 9:
        opcode = 99
    if as_char_array[-3:-2]:
        C = int( as_char_array[-3:-2] )
    else:
        C = 0
    if as_char_array[-4:-3]:
        B = int( as_char_array[-4:-3] )
    else:
        B = 0
    if as_char_array[-5:-4]:
        A = int( as_char_array[-5:-4] )
    else:
        A = 0
    return opcode, C, B, A

#  for fetching the appropriate value as per the instruction modalities
def modal_parameters ( ram, ip, modes ):
        if modes[0]:
            arg1 = ram[ip+1]
        else:
            arg1 = ram[ ram[ip+1] ]
        if modes[1]:
            arg2 = ram[ip+2]
        else:
            arg2 = ram[ ram[ip+2] ]
        # "Parameters that an instruction writes to will never be in immediate mode."
        assert modes[2] == 0
        arg3 = ram[ip+3]
        return arg1, arg2, arg3


def processor ( ram, ip, input_value ):
    opcode, mode1, mode2, mode3 = parse_opcode( ram[ip] )
    output_value = -42   # default 4 or 3 return value ... is this safe?
    if opcode in ( 1, 2, 5, 6, 7, 8 ):
        arg1, arg2, arg3 = modal_parameters( ram, ip, (mode1, mode2, mode3) )
    if   opcode == 1:
        ram[ arg3 ] = arg1 + arg2
        return ram, ip+4, output_value
    elif opcode == 2:
        ram[ arg3 ] = arg1 * arg2
        return ram, ip+4, output_value
    elif opcode == 3:
        if input_value < 0:
            output_value = -3   # this means `still running, waiting for input`
            return ram, ip, output_value    # hold on input ip
        else:
            ram[ ram[ip+1] ] = input_value
            output_value = -4   # a neg value other than -3 ??
            return ram, ip+2, output_value
    elif opcode == 4:
        output_value = ( ram[ ram[ip+1] ] )
        return ram, ip+2, output_value
    elif opcode == 5:
        if arg1:
            return ram, arg2, output_value
        else:
            return ram, ip+3, output_value
    elif opcode == 6:
        if not arg1:
            return ram, arg2, output_value
        else:
            return ram, ip+3, output_value
    elif opcode == 7:
        if arg1 < arg2:
            ram[ arg3 ] = 1
        else:
            ram[ arg3 ] = 0
        return ram, ip+4, output_value
    elif opcode == 8:
        if arg1 == arg2:
            ram[ arg3 ] = 1
        else:
            ram[ arg3 ] = 0
        return ram, ip+4, output_value
    elif opcode == 99:
        output_value = -1
        return ram, -1, output_value
    else:
        print("unknown opcode")



#  the state of any one amplifier, including its ram
class amplifier:
    def __init__( self, program, phase_setting ):
        self.program = program
        self.input_value = phase_setting
        self.phase_not_yet_set = True
        self.original_program = []
        self.original_program[:] = program[:]
        self.ip = 0

    def obtain_input( self, new_input ):
        if self.phase_not_yet_set:
            self.phase_not_yet_set = False
        else:
            self.input_value = new_input
        return

    def generate_output( self ):
        # "Don't restart the Amplifier Controller Software on any amplifier during this process" ... but that can't mean don't reset the program counter
        #self.ip = 0
        # "memory is not shared or reused between copies of the program" ... so maybe I shouldn't reload the program into ram on any one amp (?)
        #self.program[:] = self.original_program[:]
        ##
        ##   I am interpreting the puzzle to be that each amp runs an output
        ##   procedure, we record that output, then let the program continues
        ##   to run until it requires an input. At that point, we pass our output
        ##   value to the next amp and remember the ip of the input command
        ##   that is waiting. When this amp is called upon again, it will be
        ##   called with a legit input value and we jump in at the ip of the
        ##   input procedure that is hungry for it.
        ##
        output_value = 0            # `processor` returns -42 when not opcode 4
        good_output_value = -888
        while output_value not in (-1,-3):  # halted or needs to wait for input
            self.program, self.ip, output_value = \
                    processor( self.program, self.ip, self.input_value )
            if output_value >= 0:   # keep any good output, then continue program
                good_output_value = output_value
            if output_value == -1:
                good_output_value = -999     # some irrelevant value
            if good_output_value == -888 and output_value == -3:
                print( "\n attemping to enter wait mode without having outputed!" )
        return good_output_value, output_value



def thrusters( program, phase_settings ):

    # "memory is not shared or reused between copies of the program"
    Amp_A = amplifier( program, phase_settings[0] )
    Amp_B = amplifier( program, phase_settings[1] )
    Amp_C = amplifier( program, phase_settings[2] )
    Amp_D = amplifier( program, phase_settings[3] )
    Amp_E = amplifier( program, phase_settings[4] )
    amps = [ Amp_A, Amp_B, Amp_C, Amp_D, Amp_E ]

    for amp in amps:
        amp.obtain_input(0)      # initialize phase setting
    Amp_A.obtain_input(0)
    while True:
        Amp_B.obtain_input( Amp_A.generate_output()[0] )
        Amp_C.obtain_input( Amp_B.generate_output()[0] )
        Amp_D.obtain_input( Amp_C.generate_output()[0] )
        Amp_E.obtain_input( Amp_D.generate_output()[0] )
        inp_A, exit_code = Amp_E.generate_output()
        if exit_code == -1:    # if E halts (-1 rather than -3), we're done
            break
        print( " Amp A just received %d from Amp E\n" % inp_A )
        Amp_A.obtain_input( inp_A )

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

