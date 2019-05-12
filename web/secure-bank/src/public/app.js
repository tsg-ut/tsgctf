function api(path, body) {
  return fetch(path, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  }).then(res => {
    if(!res.ok) {
      return res.json().catch(_ => {
        throw {message: 'something went wrong'};
      }).then(({message}) => {
        throw {message: message || 'something went wrong'};
      });
    }
    return res;
  });
}

const app = new Vue({
  el: '#app',
  data: {
    tab: 'transfer',
    flag: '',
    info: '',
    error: '',
    logined: false,
    balance: 0,
    username: '',
    password: '',
    target: '',
    amount: '',
  },
  mounted() {
    if (localStorage.username) {
      api('/api/balance', {}).then(res => res.json()).then(({balance}) => {
        this.balance = balance;
        this.username = localStorage.username;
        this.logined = true;
      }).catch(_ => localStorage.username = '');
    }
  },
  methods: {
    updateMessage({info, error}) {
      this.info = info || '';
      this.error = error || '';
    },
    register() {
      api('/api/register', {
        user: this.username,
        pass: this.password,
      }).then(res => {
        this.updateMessage({info: 'Registered'});
      }).catch(({message}) => this.updateMessage({error: message || 'fetch error'}));
    },
    login() {
      api('/api/login', {
        user: this.username,
        pass: this.password,
      }).then(res => {
        localStorage.username = this.username;
        this.logined = true;
        this.updateMessage({info: 'Logged in'});

        return api('/api/balance', {}).then(res => res.json()).then(({balance}) => {
          this.balance = balance;
        });
      }).catch(({message}) => this.updateMessage({error: message || 'fetch error'}));
    },
    logout() {
      api('/api/logout', {}).then(res => {
        localStorage.username = '';
        this.username = '';
        this.logined = false;
        this.updateMessage({info: 'Logged out'});
      }).catch(({message}) => this.updateMessage({error: message || 'fetch error'}));
    },
    transfer() {
      api('/api/transfer', {
        target: this.target,
        amount: this.amount,
      }).then(res => res.json()).then(res => {
        this.balance = res.balance;
        this.updateMessage({info: 'Transferred'});
      }).catch(({message}) => this.updateMessage({error: message || 'fetch error'}));
    },
    getflag() {
      return fetch('/api/flag', {
        method: 'GET',
        credentials: 'include',
      }).then(res => res.json())
        .then(({flag, message}) => {
          this.flag = flag;
          this.updateMessage({error: message});
        });
    },
  }
});
