#!/usr/bin/perl

use strict;
use warnings;
use feature 'say';
use Switch;
use Scalar::Util('looks_like_number');

sub parse{
  die unless scalar @_ >= 1;
  my $version = shift;
  if( my @matches = ($version =~ m/([a-z]+|[0-9]+)/ig) ){
    return \@matches;
  }
  return 0;
}

sub compare{
  die unless scalar @_ >= 2;
  my ($a, $b) = @_;
  $a = parse($a);
  $b = parse($b);
  return -1 if !$a;
  return 1 if !$b;
  my @a = @{$a};
  my @b = @{$b};
  my $size = (scalar @a > scalar @b)? @a:@b;
  for ( my $pos=0, my $cmp; $pos<$size; $pos++ ) {
    if(defined $a[$pos] && defined $b[$pos]){
      if( looks_like_number($a[$pos]) && looks_like_number($b[$pos]) ){
        return $cmp if (($cmp = $a[$pos] <=> $b[$pos]) != 0);
      }else{
        return $cmp if (($cmp = lc $a[$pos] cmp lc $b[$pos]) != 0);
      }
    }elsif(defined $a[$pos]){
      return looks_like_number($a[$pos])? 1:-1;
    }elsif(defined $b[$pos]){
      return looks_like_number($b[$pos])? -1:1;
    }
  }
  return 0;
}

sub display{
  return unless scalar @_ >= 2;
  my ($a, $b) = @_;
  switch ( compare($a, $b) ) {
    case -1 { say "$a < $b"; }
    case  0 { say "$a = $b"; }
    case  1 { say "$a > $b"; }
  }
}

sub test{
  return unless scalar @_ >= 2;
  my ($a, $b) = @_;
  say "Error: $a $b" if compare($a, $b) == -1;
}

# use 'test' instead of 'display' for testing purposes
# when testing, use the actual higher version as the first argument
display '2.0', '1.0';
display '2.0', '2.0';
display '1.0', '0.1';
display '1.0.3', '1.0.2';
display '0.10', '0.9';
display '0.10a', '0.9b';
display '0.10a', '0.10a';
display '0.10ba', '0.10b';
display 'rc1', 'rc0';
display 'rc', 'rc';
display 'rc22', 'rc21-rc22-rc23';
display '4.0.1', '4.0.1-alpha';
display '3.2-final', '3.2-beta';
display 'b', 'a';
display 'B', 'b';
display 'FINAL', 'final';
display '0.99', '0.99dev';
display '0.100dev', '0.99';
display '0.101dev', '0.100dev';
display '0.101dev', '0.100-dev';
display '0.103rc2', '0.103-rc1';
