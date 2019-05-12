require_relative 'params'

def to_complex(x)
  a, b = x
  w = Math::E ** Complex(0, Math::PI*2.0/3.0)
  a + b*w
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

def div(x, y)
  xc, yc = to_complex(x), to_complex(y)
  a, b = (xc / yc).rect
  [(a + b/Math.sqrt(3)).round, (b*2.0/Math.sqrt(3)).round]
end

def mod(x, y)
  # many times...
  100.times do
    k = div(x, y)
    x = sub(x, mul(k, y))
  end
  x
end

def norm(x)
  a, b = x
  a*a + b*b - a*b
end

flag = "TSGCTF{XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX}"
msg  = [flag[0,flag.size/2], flag[flag.size/2,flag.size]].map {|text| text.unpack("H*")[0].hex}
modulos = MODULOS

res = modulos.map do |m|
  [mod(msg, m), m]
end

puts 'MODULOS = %p' % [modulos]
puts 'PROBLEM = %p' % [res]
