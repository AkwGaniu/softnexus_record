var app = new Vue({
  delimiters: ['[[',']]'],
  el: '#main',
  data: () => {
    return {
    current_id: 0,
    current_item: 0,
    current_date: '',
    current_data: Object,
    csrftoken: '',
    token: '',
    userActionDropDown: false,
    showModal: false,
    showAccList:  true,
    showAccEntry: false,
    showClientEntry: false,
    edit_flag: false,
    delete_flag: false,
    modalHeader: '',
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
    },
    paymentStyle: {
      width: '108px'
    }
    }
  },
  methods: {
    divSize (text) {
      let size = text.length
      size = (size + 2) / 2
      return {
        width: `${size}rem`
      }
    },
    triggerRecordEntryView (view, action)  {
      if (view ==='account' && action === 'add') {
        this.showAccEntry = true
        this.edit_flag = false
        this.modalHeader = 'Add New Account Record'
      } else if (view === 'account' && action === 'edit') {
        this.showAccEntry = true
        this.edit_flag = true
        this.modalHeader = 'Update Account Record'
      } else if (view ==='client' && action === 'add') {
        this.showClientEntry=true
        this.edit_flag = false
        this.modalHeader = 'Add New Client Record'
      } else if (view ==='client' && action === 'edit') {
        this.showClientEntry=true
        this.edit_flag = true
        this.modalHeader = 'Edit Client Record'
      }
      let date =  new Date()
      const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

      this.current_date = `${months[date.getMonth()]} ${ date.getDate()}, ${date.getFullYear()}`
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
      if (this.validateClientRecord('add_permit')){
        const data = this.validateClientRecord('add_permit')

        this.closeModal()
      let url = `/add_client_record`
      const fetchData  = {
          method: 'post',
          body: JSON.stringify(data),
          headers: {
            "Content-Type": "application/json",
            'Authorization': `Token ${this.token}`,
            'X-CSRFToken': this.csrftoken
          }
      }
      fetch(url, fetchData)
      .then(resp => {
          if(resp.ok) {
            return resp.json()
          } else {
            return Promise.reject(resp.json())
          }
      })
      .then(data => {
        console.log(data)
        this.displaySuccessMsg('Account record added')
        this.current_data = data.reply
      })
      .catch(error => {
          console.log(error.object)
      })
      }
    },
    addAccountRecord () {
      this.errorMsg = ''
      let { description, amount, type } = this.accountRecord
      if (description==='' || amount==='' || type==='') {
        this.errorMsg = 'All fields are required'
      } else if (!this.validNumber(amount)){
        this.errorMsg = 'Amount can only be numbers'
      } else {
        this.errorMsg = ''
        amount = amount + ".00"
        const data = {
          description: description,
          amount: amount,
          entry_type: type,
          user: this.current_data.user.username,
          permit: 'add_permit'
        }
        this.closeModal()

        let url = `/add_account_record`
        const fetchData  = {
            method: 'post',
            body: JSON.stringify(data),
            headers: {
              "Content-Type": "application/json",
              'Authorization': `Token ${this.token}`,
              'X-CSRFToken': this.csrftoken
            }
        }
        fetch(url, fetchData)
            .then(resp => {
                if(resp.ok) {
                  return resp.json()
                } else {
                  return Promise.reject(resp.json())
                }
            })
            .then(data => {
              this.displaySuccessMsg('Account record added')
              this.current_data = data.reply
            })
            .catch(error => {
                console.log(error.object)
            })
      }
    },
    triggerClientUpdate (id) {
      client = this.current_data.client_record.find(element => element.id === id)
      let new_amount_paid
      let new_amount_charge
      if (client.amount_paid === '0.00') {
        new_amount_paid = ''
      } else {
        let length = client.amount_paid.length
        new_amount_paid = client.amount_paid.substring(0, length - 3)
      }
      let len = client.amount_charged.length
      new_amount_charge = client.amount_charged.substring(0, len - 3)

      this.clientRecord = {
        service_offered: client.service_offered,
        name: client.client_name,
        email: client.client_email,
        phone_number: client.client_phone,
        amount_charged: new_amount_charge,
        amount_paid: new_amount_paid,
      }
      this.current_id = id
      this.triggerRecordEntryView('client', 'edit')
    },
    triggerAccountUpdate (id) {
      account = this.current_data.account_record.find(element => element.id === id)
      let len = account.amount.length
      new_amount = account.amount.substring(0, len - 3)
      this.accountRecord = {
        description: account.description,
        amount: new_amount,
        type: account.entry_type,
      }
      this.current_id = id
      this.triggerRecordEntryView('account', 'edit')
    },
    displaySuccessMsg (msg) {
      this.successMsg = msg
      setTimeout(()=> this.successMsg = '', 5000)
    },
    seekPermit () {
      this.successMsg = 'Access Denied. Please contact admin'
      setTimeout(()=> this.successMsg = '', 5000)
    },
    updateClientRecord () {
      this.errorMsg = ''
      if (this.validateClientRecord('edit_permit')){
        const data = this.validateClientRecord('edit_permit')

        this.closeModal()
        let url = `/update_client_record`
        const fetchData  = {
            method: 'put',
            body: JSON.stringify(data),
            headers: {
              "Content-Type": "application/json",
              'Authorization': `Token ${this.token}`,
              'X-CSRFToken': this.csrftoken
            }
        }
        fetch(url, fetchData)
            .then(resp => {
                if(resp.ok) {
                  return resp.json()
                } else {
                  return Promise.reject(resp.json())
                }
            })
            .then(data => {
              console.log(data)
              this.displaySuccessMsg('Client record updated')
              this.current_data = data.reply
            })
            .catch(error => {
                console.log(error.object)
            })
        
      }
    },
    updateAccountRecord () {
      this.errorMsg = ''
      let { description, amount, type } = this.accountRecord
      if (description==='' || amount==='' || type==='') {
        this.errorMsg = 'All fields are required'
      } else if (!this.validNumber(amount)){
        this.errorMsg = 'Amount can only be numbers'
      } else {
        this.errorMsg = ''
        amount = amount + ".00"

        const data = {
          description: description,
          amount: amount,
          entry_type: type,
          user: this.current_data.user.username,
          id: this.current_id,
          permit: 'edit_permit'
        }
        this.closeModal()

        let url = `/update_account_record`
        const fetchData  = {
            method: 'put',
            body: JSON.stringify(data),
            headers: {
              "Content-Type": "application/json",
              'Authorization': `Token ${this.token}`,
              'X-CSRFToken': this.csrftoken
            }
        }
        fetch(url, fetchData)
        .then(resp => {
            if(resp.ok) {
              return resp.json()
            } else {
              return Promise.reject(resp.json())
            }
        })
        .then(data => {
          this.displaySuccessMsg('Account record updated')
          this.current_data = data.reply
        })
        .catch(error => {
            console.log(error.object)
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
      let url = `/delete_record`
      const fetchData  = {
          method: 'delete',
          body: JSON.stringify(payload),
          headers: {
            "Content-Type": "application/json",
            'Authorization': `Token ${this.token}`,
            'X-CSRFToken': this.csrftoken
          }
      }
      fetch(url, fetchData)
      .then(resp => {
          if(resp.ok) {
            return resp.json()
          } else {
            return Promise.reject(resp.json())
          }
      })
      .then(data => {
        this.displaySuccessMsg('Record deleted')
        this.current_data = data.reply
      })
      .catch(error => {
          console.log(error.object)
      })
    },
    generateInvoice (id) {

      // let payload = {
      //   client_id: id
      // }

      let url = `/generate_invoice/${id}`
      // const fetchData  = {
      //     method: 'get',
      //     body: JSON.stringify(payload),
      //     // headers: {
      //     //   "Content-Type": "application/json",
      //     //   'Authorization': `Token ${this.token}`,
      //     //   'X-CSRFToken': this.csrftoken
      //     // }
      // }
      fetch(url)
      .then(resp => {
          if(resp.ok) {
            return resp.json()
          } else {
            return Promise.reject(resp.json())
          }
      })
      .then(data => {
        console.log(data)
      })
      .catch(error => {
          console.log(error.object)
      })
    },
    validEmail(email) {
      const regex = /^\S+@\S+\.\S+$/;
      if(regex.test(email) === false) {
          return false
      } else{
        return true
      }
    },
    validText (text) {
      const regex = /^[a-zA-Z\s]+$/;                
        if(regex.test(text) === false) {
          return false
        } else {
          return true
        }
    },
    validNumber (text) {
      const regex = /^[0-9\s]+$/;                
        if(regex.test(text) === false) {
          return false
        } else {
          return true
        }
    },
    validPhoneNumber (number) {
      const regex = /^(?=.*[0])(?=.*[0-9])(?=.*[0-1])(?=.*[0-9])(?=.{11,})/
      if(regex.test(number) === false) {
        return false
      } else{
        return true
      }
    },
    validateClientRecord(action_permit) {
      let { service_offered, name, email, phone_number, amount_charged, amount_paid } = this.clientRecord
      if (service_offered==='' || name==='' || email==='' || amount_charged==='') {
        this.errorMsg = 'Please fill out the required fields'
        return false
      } else if (!this.validText(name)){
        this.errorMsg = 'Name field can only be text'
        return false
      } else if (!this.validEmail(email)) {
        this.errorMsg = 'Please enter a valid email'
        return false
      } else if (phone_number.length > 0 && !this.validPhoneNumber(phone_number)){
        this.errorMsg = 'Please provide a valid phone number'
        return false
      } else if (!this.validNumber(amount_charged)){
        this.errorMsg = 'Amount can only be numbers'
        return false
      }else if (amount_paid.length > 0 && !this.validNumber(amount_paid)){
        this.errorMsg = 'Amount can only be numbers'
        return false
      }else {
        amount_paid.length ? amount_paid = amount_paid + ".00" : amount_paid = amount_paid + "0.00"
        amount_charged = amount_charged + ".00" 
        this.errorMsg = ''
        let data = {}
        if (action_permit === 'edit_permit') {
          data = {
            service: service_offered,
            name: name,
            email: email,
            phone: phone_number,
            amount_charged: amount_charged,
            amount_paid: amount_paid,
            user: this.current_data.user.username,
            id: this.current_id,
            permit: action_permit,
          }
        } else {
          data = {
            service: service_offered,
            name: name,
            email: email,
            phone: phone_number,
            amount_charged: amount_charged,
            amount_paid: amount_paid,
            user: this.current_data.user.username,
            permit: action_permit,
          }
        }
        return data
      }
    },
    getToken() {
      axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
          let token = document.head.querySelector('meta[name="csrf-token"]');

          if (token) {
            this.csrftoken = token.content
            axios.defaults.headers.common['X-CSRF-TOKEN'] = token.content;
          } else {
              console.error('CSRF token not found: https://laravel.com/docs/csrf#csrf-x-csrf-token');
          }
    }
    },
    created () {
      const data = localStorage.getItem('user')
      if (data !== null) {
        userData = JSON.parse(data)
        axios.get('/get_data', {
          params: {user: userData.user}
        })
        .then((response) => {
         this.current_data = response.data.reply
         this.token = userData.token
        })
        .catch((error) => {
          console.log(error)
        })
      } else {
        self.location = '/logout_user'
      }
      this.getToken()
    }
})