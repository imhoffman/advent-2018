!! *** Advent of Code 2019 Day 04

!!
!! subroutines and functions
!!
 module subs
  implicit none
  contains

  !!
  !! puzzle ruleset
  !!

  !!  parse integer into a char arraay
  function as_char_array ( as_integer ) result ( ca )
    character(6)        :: ca
    integer, intent(in) :: as_integer
    character           :: c
    integer             :: i, j, n, current_modulus

    n = as_integer
    j = 0
    do i = 5, 0, -1
      current_modulus = mod( n, int( 10**i ) )
      write( c, '(I1)' ) ( n - current_modulus )/10**i
      n = current_modulus
      j = j + 1
      ca(j:j) = c
    end do

    return
  end function as_char_array


  !!  test for increasing digit values
  recursive function is_increasing ( as_integer ) result ( predicate )
    integer, intent(in)        :: as_integer
    logical                    :: predicate
    integer                    :: i, a, b, current_modulus, n

    n = as_integer
    do i = 5, 1, -1
      current_modulus = mod( n, int( 10**i ) )
      a = ( n - current_modulus )/10**i
      n = current_modulus
      current_modulus = mod( n, int( 10**(i-1) ) )
      b = ( n - current_modulus )/10**(i-1)
      if ( a .gt. b ) then
        predicate = .false.
        goto 100
      endif
    end do

    predicate = .true.
    100 continue
    return
  end function is_increasing


  !!  test for repetitions as per rules
  recursive function has_repeat ( as_integer, repeat_counting_array ) result ( predicate )
    integer, intent(in)        :: as_integer
    integer, intent(inout)     :: repeat_counting_array(10)
    logical                    :: predicate
    character(:), allocatable  :: chars
    integer, allocatable       :: as_integer_array(:)
    integer                    :: i, j, num_chars, integer_for_recur

    chars = as_char_array( as_integer )
    num_chars = len( chars )
    allocate( as_integer_array(num_chars) )
    integer_for_recur = 0

    !!  terminal case: we have recurred down to one digit
    if ( num_chars .eq. 1 ) then
      do i = 1, 10
        if ( repeat_counting_array(i) .eq. 1 ) then
          predicate = .true.
        else
          predicate = .false.
        endif
      enddo
    else
    !!  recursive case
      do i = 1, num_chars-1
        if ( as_integer_array(i) .eq. as_integer_array(i+1) ) then
          j = as_integer_array(i)
          repeat_counting_array(j) = repeat_counting_array(j) + 1
          do j = num_chars, 1, -1
            integer_for_recur = integer_for_recur + as_integer_array(j)*10**(j-1)
          enddo
        endif
      enddo
      predicate = has_repeat( integer_for_recur, repeat_counting_array )
    endif

    deallocate( as_integer_array )
    return
  end function has_repeat

  function apply_rules ( lower_bound, upper_bound ) result ( possible )
    integer, intent(in)  :: lower_bound, upper_bound
    logical              :: possible( upper_bound - lower_bound )

    possible(1) = .true.
    return
  end function apply_rules
 end module subs

!!
!! main program
!!
 program main
  use subs
  implicit none
  integer :: upper_bound, lower_bound
  integer :: repeat_counting_array(10)
  integer :: test

  ! read puzzle input --- always six-digit integers
  open( 10, file="puzzle.txt")
  read( 10, '(I6,1X,I6)' ) lower_bound, upper_bound
  close( 10 )

  write(6,'(/,A,I0,A,I0,A,/)') ' Using ', lower_bound, ' and ', upper_bound, ' as bounds.'

  repeat_counting_array(:) = 0
  !test = lower_bound
  test = 123456
  write(6,*) test, " is increasing? ", is_increasing( test )
  write(6,*) test, "   is repeat-y? ", has_repeat( test, repeat_counting_array )

  stop
 end program main

