#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import findall

def parse(version):
  matches = findall('([aA-zZ]+|[0-9]+)', str(version))
  if matches:
    for match in matches:
      try:
        matches[matches.index(match)] = int(match)
      except:
        matches[matches.index(match)] = match.lower()
    return matches
  else:
    return False

def compare(fversion, sversion):
  fmatches = parse(fversion)
  smatches = parse(sversion)
  if not fmatches:
    return -1
  elif not smatches:
   return 1
  if all(isinstance(elem, str) for elem in fmatches) and all(isinstance(elem, str) for elem in smatches):
    fmatches = ''.join(fmatches)
    smatches = ''.join(smatches)
    if fmatches > smatches:
      return 1
    elif fmatches < smatches:
      return -1
    else:
      return 0
  size = len(fmatches) if len(fmatches) > len(smatches) else len(smatches)
  for x in range(0, size):
    try:
      if fmatches[x] > smatches[x]:
        return 1
      elif fmatches[x] < smatches[x]:
        return -1
    except IndexError:
      try:
        return 1 if isinstance(fmatches[x], int) else -1
      except IndexError:
        try:
          return -1 if isinstance(smatches[x], int) else 1
        except IndexError:
          pass
  return 0

# Always use the actual higher version as the first argument when using this
def test(fversion, sversion):
  if compare(fversion, sversion) == -1:
    print("Error: '{0}' < '{1}', but it shouldn't be.".format(fversion, sversion))
    return False
  else:
    return True

def tests():
  test('0.10', '0.9');
  test('0.100dev', '0.99');
  test('0.101dev', '0.100-dev');
  test('0.101dev', '0.100dev');
  test('0.103rc2', '0.103-rc1');
  test('0.10a', '0.10a');
  test('0.10a', '0.9b');
  test('0.10ba', '0.10b');
  test('0.99', '0.99dev');
  test('0100', '0100dev');
  test('1.0', '0.1');
  test('1.0.3', '1.0.2');
  test('10-0-2', '9-10-2');
  test('2.0', '1.0');
  test('2.0', '2.0');
  test('2028-1', '2028-1a');
  test('20281', '20281a');
  test('3.2-final', '3.2-beta');
  test('4.0.1', '4.0.1-alpha');
  test('B', 'b');
  test('FINAL', 'final');
  test('alpha', 'a');
  test('alpha', 'a-1');
  test('alpha', 'a-11');
  test('alpha', 'a1');
  test('b', 'a');
  test('pre-alpha', 'prealpha');
  test('pre-alpha1', 'pre-alpha0');
  test('prealpha1', 'pre-alpha0');
  test('prealpha1', 'prealpha0');
  test('rc', 'rc');
  test('rc-----10', 'rc--10----');
  test('rc-----10', 'rc10');
  test('rc-----20', 'rc---');
  test('rc-----20', 'rc10');
  test('rc1', 'rc-1');
  test('rc1', 'rc0');
  test('rc21-rc22-rc23', 'rc21rc22rc23');
  test('rc22', 'rc21-rc22-rc23');
  test('rc3', 'rc1');

if __name__ == '__main__':
  tests()
