require 'securerandom'
require 'set'

alias :pp :p

def miller_rabin(n)
  raise ArgumentError unless n >= 2
  return true if n == 2
  return false if n == 1 or n.even?
  return n != 9 if n < 15

  d, r = n-1, 0
  while d.even?
    d >>= 1
    r += 1
  end

  30.times do
    a = rand(2..(n-2))
    x = a.pow(d, n)

    ok = false
    next if x == 1 or x == n-1
    (r-1).times do
      x = (x*x) % n
      if x == n-1
        ok = true
        break
      end
    end

    return false unless ok
  end

  true
end

def getprime(bits)
  loop do
    p = SecureRandom.random_number(1<<bits)
    return p if miller_rabin(p)
  end
end

bits = 4096
p, q = 2.times.map{getprime(bits)}

X = p^q
N = p*q

# puts X.to_s(2)
# puts N.to_s(2)

puts p, q

p, q = 0, 0

tbl = [[[0,0],[1,1]], [[0,1],[1,0]]]

def dfs(p, q, i)
  pp [p, q] if i < 0
  
  n, m = 1<<i, (1<<i) - 1

  case X[i]
  when 0
    dfs(p, q, i-1) if p * q <= N and N <= (p+m) * (q+m)
    dfs(p+n, q+n, i-1) if (p+n) * (q+n) <= N and N <= (p+m+n) * (q+m+n)
  when 1
    dfs(p+n, q, i-1) if (p+n) * q <= N and N <= (p+m+n) * (q+m)
    dfs(p, q+n, i-1) if p * (q+n) <= N and N <= (p+m) * (q+m+n)
  end
end

dfs(0, 0, 4096)
