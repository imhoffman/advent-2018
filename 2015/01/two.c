// *** Advent of Code 2015 Day 01
#include<stdio.h>
#include<stdlib.h>
#include<string.h>

#define MAXCHARS 65536

//  file-reader subroutine to determine dynamic lengths
void reader( FILE *f, int *n, char file_contents[] ) {
  char buffer[MAXCHARS] = { '\0' };
  int num_lines = 0;
  char *qnull;
  size_t file_length;

  while ( fgets( buffer, MAXCHARS, f ) != NULL ) {
    strncpy( file_contents, buffer, MAXCHARS );
    num_lines = num_lines + 1;
  }

  if ( num_lines > 1 ) {
	  printf( "\n PROBLEM: more than one line in file\n" );
	  *n = -1;
	  return;
  }

  qnull = strchr( file_contents, '\0' );
  file_length = qnull - &file_contents[0];   // difference of size_t's
  *n =(int) file_length;

  return;
}


//  part two ruleset
//  i = 1 and floor = 0 are the puzzle initial conditions
int basement_finder( const char directions[], const int num_directions ) {
  int i = 1, floor = 0;

  while ( floor != -1  &&  i < num_directions+1 ) {
    if      ( directions[i-1] == '(' ) { floor++; i++; }
    else if ( directions[i-1] == ')' ) { floor--; i++; }
    else { printf( "\n problem reading directions\n" ); }
  }

  //  return one fewer b/c increment occurs after the find
  return i-1;
}



//
// main program
//
int main( int argc, char *argv[] ) {
  FILE* fp;
  int nchars;

  char *temp;
  temp =(char *) malloc( MAXCHARS * sizeof( char ) );

  fp = fopen("puzzle.txt","r");
  reader( fp, &nchars, temp);
  fclose(fp);

  char *directions = malloc( (nchars+1) * sizeof( char ) );
  strncpy( directions, temp, nchars );
  free( temp );     // free the huge temporary file-read buffer
  directions[nchars+1] = '\0';    // in this needed ?

  printf( "\n first encountered floor -1 at direction number %d\n\n", 
		basement_finder( directions, nchars ) );

  return 0;
}
