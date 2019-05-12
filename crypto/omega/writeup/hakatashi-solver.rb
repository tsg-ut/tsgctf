require_relative '../params'

def to_complex(x)
  a, b = x
  w = Math::E ** Complex(0, Math::PI*2.0/3.0)
  a + b*w
end

def add(x, y)
  a, b = x
  c, d = y
  [a+c, b+d]
end

def sub(x, y)
  a, b = x
  c, d = y
  [a-c, b-d]
end

def mul(x, y)
  a, b = x
  c, d = y
  [a*c - b*d, a*d + b*c - b*d]
end

#def div(x, y)
  #xc, yc = to_complex(x), to_complex(y)
  #a, b = (xc / yc).rect
  #[(a + b/Math.sqrt(3)).round, (b*2.0/Math.sqrt(3)).round]
#end

def rounddiv(a, b)
  c = a / b
  remainder = a - b * c
  if (remainder * 2).abs < b.abs
    c
  else
    c + 1
  end
end

def div(x, y)
  a, b = x
  c, d = y
  n = norm(y)
  [rounddiv(a * c + b * d - a * d, n), rounddiv(b * c - a * d, n)]
end

def mod(x, y)
  k = div(x, y)
  x = sub(x, mul(k, y))
  x
end

def norm(x)
  a, b = x
  a*a + b*b - a*b
end

def gcd(a, b)
  if b[0] == 0 && b[1] == 0
    return [a, [1, 0], [0, 0]]
  end

  d, q, p = gcd(b, mod(a, b))
  q = sub(q, mul(div(a, b), p))
  return d, p, q
end

def chinese(values, modulos)
  r = [0, 0]
  m = [1, 0]
  values.zip(modulos).each do |value, modulo|
    d, p, q = gcd(m, modulo)
    v = mod(sub(value, r), d)
    if v[0] != 0 || v[1] != 0
      return 'invalid'
    end
    tmp = mod(mul(div(sub(value, r), d), p), div(modulo, d))
    r = add(r, mul(m, tmp))
    m = mul(m, div(modulo, d))
    #p mod(value, modulo), mod(r, modulo)
  end
  mod(r, m)
end

v = chinese(PROBLEM.map {|i, m| i}, PROBLEM.map {|i, m| m})

puts([v[0].to_s(16)].pack('H*') + [v[1].to_s(16)].pack('H*'))
