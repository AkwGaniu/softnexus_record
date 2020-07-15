var app = new Vue({
  delimiters: ['[[',']]'],
  el: '#main',
  data: () => {
    return {
    current_id: 0,
    current_data: Object,
    userActionDropDown: false,
    showModal: false,
    showAccList:  true,
    showAccEntry: false,
    showClientEntry: false,
    edit_flag: false,
    delete_flag: false,
    delete_table: '',
    errorMsg: '',
    successMsg: '',
    clientRecord: {
      service_offered: '',
      name: '',
      email: '',
      phone_number: '',
      amount_charged: '',
      amount_paid: '',
    },
    accountRecord: {
      description: '',
      amount: '',
      type: '',
    }
    }
  },
  methods: {
    triggerRecordEntryView (view, action)  {
      if (view ==='account' && action === 'add') {
        this.showAccEntry = true
        this.edit_flag = false
      } else if (view ==='account' && action === 'edit') {
        this.showAccEntry = true
        this.edit_flag = true
      } else if (view ==='client' && action === 'add') {
        this.showClientEntry=true
        this.edit_flag = false
      } else if (view ==='client' && action === 'edit') {
        this.showClientEntry=true
        this.edit_flag = true
      }
      this.showModal = !this.showModal
    },

    closeModal () {
      this.showModal = !this.showModal
      this.showAccEntry = false
      this.showClientEntry = false
      this.current_id = 0
      this.clientRecord = {
        service_offered: '',
        name: '',
        email: '',
        phone_number: '',
        amount_charged: '',
        amount_paid: '',
      }
      this.accountRecord = {
        description: '',
        amount: '',
        type: '',
      }
    },

    addClientRecord () {
      this.errorMsg = ''
      const { service_offered, name, email, phone_number, amount_charged, amount_paid } = this.clientRecord
      if (service_offered==='' || name==='' || email==='' || amount_charged==='') {
        this.errorMsg = 'Please fill out the required fields'
      }else {
        this.errorMsg = ''
        const data = {
          service: service_offered,
          name: name,
          email: email,
          phone: phone_number,
          amount_charged: amount_charged,
          amount_paid: amount_paid,
          user: this.current_data.user.username,
          permit: 'add_permit'
        }
        this.showModal = !this.showModal
        this.clientRecord = {
          service_offered: '',
          name: '',
          email: '',
          phone_number: '',
          amount_charged: '',
          amount_paid: '',
        }
        axios.post('/add_client_record', data)
        .then((response) => {
          if (response.data.reply = 'success') {
            this.successMsg = 'Client record added'
          }
        })
        .catch((error) => {
          console.log(error)
        })
      }
    },
    addAccountRecord () {
      this.errorMsg = ''
      const { description, amount, type } = this.accountRecord
      if (description==='' || amount==='' || type==='') {
        this.errorMsg = 'All fields are required'
      }else {
        this.errorMsg = ''
        const data = {
          description: description,
          amount: amount,
          entry_type: type,
          user: this.current_data.user.username,
          permit: 'add_permit'
        }

        this.showModal = !this.showModal
        this.accountRecord = {
          description: '',
          amount: '',
          type: '',
        }

        axios.post('/add_account_record', data)
        .then((response) => {
            this.successMsg = 'Account record added'
            this.current_data = response.data.reply
        })
        .catch((error) => {
          console.log(error)
        })
      }
    },
    triggerClientUpdate (id) {
      client = this.current_data.client_record.find(element => element.id === id)
      this.clientRecord = {
        service_offered: client.service_offered,
        name: client.client_name,
        email: client.client_email,
        phone_number: client.client_phone,
        amount_charged: client.amount_charged,
        amount_paid: client.amount_paid,
      }
      this.current_id = id
      this.triggerRecordEntryView('client', 'edit')
    },
    triggerAccountUpdate (id) {
      account = this.current_data.account_record.find(element => element.id === id)
      this.accountRecord = {
        description: account.description,
        amount: account.amount,
        type: account.entry_type,
      }
      this.current_id = id
      this.triggerRecordEntryView('account', 'edit')
    },
    seekPermit () {
      this.successMsg = 'Access Denied. Please contact admin'
      setTimeout(()=> this.successMsg = '', 5000)
    },
    updateClientRecord () {
      this.errorMsg = ''
      const { service_offered, name, email, phone_number, amount_charged, amount_paid } = this.clientRecord
      if (service_offered==='' || name==='' || email==='' || amount_charged==='') {
        this.errorMsg = 'Please fill out the required fields'
      }else {
        this.errorMsg = ''
        const data = {
          service: service_offered,
          name: name,
          email: email,
          phone: phone_number,
          amount_charged: amount_charged,
          amount_paid: amount_paid,
          user: this.current_data.user.username,
          id: this.current_id,
          permit: 'edit_permit'
        }
        this.showModal = !this.showModal
        this.current_id = 0
        this.clientRecord = {
          service_offered: '',
          name: '',
          email: '',
          phone_number: '',
          amount_charged: '',
          amount_paid: '',
        }
        axios.put('/update_client_record', data)
        .then((response) => {
          this.successMsg = 'Client record updated'
          this.current_data = response.data.reply
        })
        .catch((error) => {
          console.log(error)
        })
      }

    },
    updateAccountRecord () {
      this.errorMsg = ''
      const { description, amount, type } = this.accountRecord
      if (description==='' || amount==='' || type==='') {
        this.errorMsg = 'All fields are required'
      }else {
        this.errorMsg = ''
        const data = {
          description: description,
          amount: amount,
          entry_type: type,
          user: this.current_data.user.username,
          id: this.current_id,
          permit: 'edit_permit'
        }
        this.showModal = !this.showModal
        this.current_id = 0
        this.accountRecord = {
          description: '',
          amount: '',
          type: '',
        }

        axios.put('/update_account_record', data)
        .then((response) => {
          this.successMsg = 'Account record updated'
          this.current_data = response.data.reply
        })
        .catch((error) => {
          console.log(error)
        })
      }
    },
    triggerDelete (id, table) {
      this.current_id = id
      this.delete_flag = true
      this.delete_table = table
    },
    cancelDelete() {
      this.current_id = 0
      this.delete_flag = false
      this.delete_table = ''
    },
    deleteRecord() {
      let table
      if (this.current_id !== 0 && this.delete_table === 'client') {
         table = 'Client'
      } else if (this.current_id !== 0 && this.delete_table === 'account') {
        table = 'Account'
      }
      let payload = {
        id: this.current_id,
        table: table,
        user: this.current_data.user.username,
        permit: 'delete_permit'
      }

      this.current_id = 0
      this.delete_flag = false
      this.delete_table = ''

        axios.delete('/delete_record', {data: payload})
        .then((response) => {
          this.current_data = response.data.reply
          this.successMsg = 'Record deleted'
        })
        .catch((error) => {
          console.log(error)
        })
    }
  },
  created () {
    user = JSON.parse(localStorage.getItem('user'))
    axios.get('/get_data', {params: user})
        .then((response) => {
         this.current_data = response.data.reply
        })
        .catch((error) => {
          console.log(error)
    })
  }
})