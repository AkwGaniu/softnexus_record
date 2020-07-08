var app = new Vue({
  delimiters: ['[[',']]'],

  el: '#login_app',
  data: {
    message: 'Hello Vue!',
    data_from_template: data
  },

  methods: {
    sayHi: () => {
      alert('Hey we are here')
    }
  },

  mounted: function () {

    console.log(this.data_from_template.name)
  }
})