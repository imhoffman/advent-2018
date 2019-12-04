#!/usr/bin/env python3

##
##  subprograms
##

def is_increasing ( string_of_digits ):
    if len( string_of_digits ) == 1:
        return True
    for i in range( len( string_of_digits ) ):
        for j in range( i+1, len( string_of_digits )-i ):
            if int(string_of_digits[i]) > int(string_of_digits[j]):
                return False
            else:
                return is_increasing( string_of_digits[1:] )


def has_repeats ( string_of_digits ):
    if len( string_of_digits ) == 1:
        return False
    for i in range( len( string_of_digits )-1 ):
        if int( string_of_digits[i] ) == int( string_of_digits[i+1] ):
            return True
        else:
            return has_repeats ( string_of_digits[1:] )


def rules ( lower_bound, upper_bound ):
    list_of_possibilities = []
    for i in range( lower_bound, upper_bound ):
        candidate_digits = str( i )
        if not is_increasing( candidate_digits ):
            continue
        if not has_repeats( candidate_digits ):
            continue
        list_of_possibilities.append( i )
    return list_of_possibilities


##
##  main program
##

with open("puzzle.txt") as fo:
  puzzle = fo.readline().strip()
#fo.close()

print( "\n read %d characters from input file\n" % ( len(puzzle) ) )

lower_bound = int( puzzle[:5] )
upper_bound = int( puzzle[7:] )

possibilities = rules( lower_bound, upper_bound )

print( "\n number of possible passwords: %d\n\n" % len( possibilities ) )


