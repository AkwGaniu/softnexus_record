var app = new Vue({
  delimiters: ['[[',']]'],
  el: '#main',
  data: () => {
    return {
    counter: 0,
    current_data: Data,
    userActionDropDown: false,
    showModal: false,
    showAccList:  true,
    showAccEntry: false,
    showClientEntry: false,
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
      amount: 0.0,
      type: '',
      // entry_date: Date
    }
    }
  },
  methods: {
    triggerRecordEntryView (view)  {
      view ==='account' ? this.showAccEntry = true : this.showClientEntry=true
      this.showModal = !this.showModal
    },

    closeModal () {
      this.showModal = !this.showModal
      this.showAccEntry = false,
      this.showClientEntry = false,
      this.clientRecord = {
        service_offered: '',
        name: '',
        email: '',
        phone_number: '',
        amount_charged: '',
        amount_paid: '',
      }
    },

    submitForm () {
      this.errorMsg = ''
      const { service_offered, name, email, phone, amount_charged, amount_paid } = this.clientRecord
      if (service_offered==='' || name==='' || email==='' || amount_charged==='') {
        this.errorMsg = 'Please fill out the required fields'
      }else {
        this.errorMsg = ''
        const data = {
          service: this.clientRecord.service_offered,
          name: this.clientRecord.name,
          email: this.clientRecord.email,
          phone: this.clientRecord.phone_number,
          amount_charged: this.clientRecord.amount_charged,
          amount_paid: this.clientRecord.amount_paid,
          user: this.current_user.username,
          permit: 'add_permit'
        }
        console.log('hey there')
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
            this.successMsg = 'Client record added successfully'
          }
        })
        .catch((error) => {
          console.log(error)
        })
      }
    },
    triggerEdit(id) {
      client = this.current_data.client_record.find(element => element.id === id)
      this.clientRecord = {
        service_offered: client.service_offered,
        name: client.client_name,
        email: client.client_email,
        phone_number: client.client_phone,
        amount_charged: client.amount_charged,
        amount_paid: client.amount_paid,
      }
      this.triggerRecordEntryView('client')
    },
    seekPermit() {
      this.successMsg = ':)Access Denied. please contact admin for help'
    }
  },

  mounted: function () {
    console.log(this.current_data)
  }
})