srand(68)

UNITS = [[0,1],[0,-1],[1,0],[-1,0],[1,1],[-1,-1]]

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

def scalar(k)
  [k, 0]
end

def mul(*xs)
  r = [1, 0]
  xs.each do |x|
    a, b = r
    c, d = x
    r = [a*c - b*d, a*d + b*c - b*d]
  end
  r
end

def div(x, y)
  xc, yc = to_complex(x), to_complex(y)
  a, b = (xc / yc).rect
  [(a + b/Math.sqrt(3)).round, (b*2.0/Math.sqrt(3)).round]
end

def mod(x, y)
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

flag = "TSGCTF{I_H34RD_S0ME_IN7EGERS_INCLUDING_EISENSTEIN'S_F0RM_EUCL1DE4N_R1NG!}"
msg  = [flag[0,flag.size/2], flag[flag.size/2,flag.size]].map {|text| text.unpack("H*")[0].hex}

def extgcd(a, b)
  if b == [0, 0]
    case a
    when [1,0]
      {x: [1,0], y: [0,0], gcd: [1,0]}
    when [-1,0]
      {x: [-1,0], y: [0,0], gcd: [1,0]}
    when [0,1]
      {x: [-1,-1], y: [0,0], gcd: [1,0]}
    when [0,-1]
      {x: [1,1], y: [0,0], gcd: [1,0]}
    when [1,1]
      {x: [0,-1], y: [0,0], gcd: [1,0]}
    when [-1,-1]
      {x: [0,1], y: [0,0], gcd: [1,0]}
    else
      {x: [1,0], y: [0,0], gcd: a}
    end
  else
    k = div(a, b)
    prev = extgcd(b, sub(a, mul(k, b)))

    {
      x: prev[:y],
      y: sub(prev[:x], mul(k, prev[:y])),
      gcd: prev[:gcd]
    }
  end
end

modulos = 20.times.inject([]){|s, _|
  x = nil
  loop do
    x = [rand(1000000), rand(1000000)]
    break if s.all?{|y| UNITS.include? extgcd(x, y)[:gcd]}
  end
  s << x
}

res = modulos.map do |m|
  [mod(msg, m), m]
end

puts 'MODULOS = %p' % [modulos]
puts 'PROBLEM = %p' % [res]
