require 'digest/sha1'
require 'rack/contrib'
require 'sinatra/base'
require 'sinatra/json'
require 'sqlite3'

STRETCH = 1000
LIMIT   = 1000

class App < Sinatra::Base
  DB = SQLite3::Database.new 'data/db.sqlite3'
  DB.execute <<-SQL
    CREATE TABLE IF NOT EXISTS account (
      user TEXT PRIMARY KEY,
      pass TEXT,
      balance INTEGER
    );
  SQL

  use Rack::PostBodyContentTypeParser
  enable :sessions

  def err(code, message)
    [code, json({message: message})]
  end

  not_found do
    redirect '/index.html', 302
  end

  get '/source' do
    content_type :text

    IO.binread __FILE__
  end

  get '/api/flag' do
    return err(401, 'login first') unless user = session[:user]

    hashed_user = STRETCH.times.inject(user){|s| Digest::SHA1.hexdigest(s)}

    res = DB.query 'SELECT balance FROM account WHERE user = ?', hashed_user
    row = res.next
    balance = row && row[0]
    res.close

    return err(401, 'login first') unless balance
    return err(403, 'earn more coins!!!') unless balance >= 10_000_000_000

    json({flag: IO.binread('data/flag.txt')})
  end

  post '/api/balance' do
    return err(401, 'login first') unless user = session[:user]

    hashed_user = STRETCH.times.inject(user){|s| Digest::SHA1.hexdigest(s)}
    res = DB.query('SELECT balance FROM account WHERE user = ?', hashed_user)
    row = res.next
    res.close

    return err(401, 'login first') unless row

    json({balance: row[0]})
  end

  post '/api/register' do
    return err(400, 'bad request') unless user = params[:user] and String === user
    return err(400, 'bad request') unless pass = params[:pass] and String === pass

    return err(400, 'too short username') unless 4 <= user.size
    return err(400, ':thinking_face: 🤔') unless 6 <= pass.size
    return err(400, 'too long request') unless user.size <= LIMIT and pass.size <= LIMIT

    sleep 1

    hashed_user = STRETCH.times.inject(user){|s| Digest::SHA1.hexdigest(s)}
    hashed_pass = STRETCH.times.inject(pass){|s| Digest::SHA1.hexdigest(s)}

    begin
      DB.execute 'INSERT INTO account (user, pass, balance) VALUES (?, ?, 100)', hashed_user, hashed_pass
    rescue SQLite3::ConstraintException
      return err(422, 'the username has already been taken')
    end

    return 200
  end

  post '/api/login' do
    return err(400, 'bad request') unless user = params[:user] and String === user
    return err(400, 'bad request') unless pass = params[:pass] and String === pass

    return err(400, 'too short username') unless 4 <= user.size
    return err(400, ':thinking_face: 🤔') unless 6 <= pass.size
    return err(400, 'too long request') unless user.size <= LIMIT and pass.size <= LIMIT

    hashed_user = STRETCH.times.inject(user){|s| Digest::SHA1.hexdigest(s)}
    hashed_pass = STRETCH.times.inject(pass){|s| Digest::SHA1.hexdigest(s)}

    res = DB.query 'SELECT 1 FROM account WHERE user = ? AND pass = ?', hashed_user, hashed_pass
    row = res.next
    res.close

    return err(401, 'username and password did not match') unless row

    session[:user] = user
    return 200
  end

  post '/api/logout' do
    session[:user] = nil
    return 200
  end

  post '/api/transfer' do
    return err(401, 'login first') unless src = session[:user]

    return err(400, 'bad request') unless dst = params[:target] and String === dst and dst != src
    return err(400, 'bad request') unless amount = params[:amount] and String === amount
    return err(400, 'bad request') unless amount = amount.to_i and amount > 0

    sleep 1

    hashed_src = STRETCH.times.inject(src){|s| Digest::SHA1.hexdigest(s)}
    hashed_dst = STRETCH.times.inject(dst){|s| Digest::SHA1.hexdigest(s)}

    res = DB.query 'SELECT balance FROM account WHERE user = ?', hashed_src
    row = res.next
    balance_src = row && row[0]
    res.close
    return err(422, 'no enough coins') unless balance_src >= amount

    res = DB.query 'SELECT balance FROM account WHERE user = ?', hashed_dst
    row = res.next
    balance_dst = row && row[0]
    res.close
    return err(422, 'no such user') unless balance_dst

    balance_src -= amount
    balance_dst += amount

    DB.execute 'UPDATE account SET balance = ?  WHERE user = ?', balance_src, hashed_src
    DB.execute 'UPDATE account SET balance = ?  WHERE user = ?', balance_dst, hashed_dst

    json({amount: amount, balance: balance_src})
  end
end
