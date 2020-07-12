var app = new Vue({
  delimiters: ['[[',']]'],
  el: '#main',
  
  data: () => {
    return {
    message: 'Hello Vue!',
    current_user: userData,
    userActionDropDown: false,
    showModal: false,
    showAccList:  true,
    showAccEntry: false,
    showClientEntry: false
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
      this.showClientEntry = false
    }
  },

  mounted: function () {
    console.log(this.current_user.username)
  }
})