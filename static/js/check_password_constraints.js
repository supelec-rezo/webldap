/**
 * CHECK PASSWORD CONSTRAINTS
 * Check if a password respects the LDAP password constraints
 * See length constraints of LDAP passwords at ou=Policies,dc=rezomen,dc=fr
 * See passwords class constraints at /etc/ldap/ppolicy.conf
 */

function check_password_constraints(){
  var passwordInput = $('#id_passwd');

  passwordInput.on('input', function(e){
    var newValue = $(e.currentTarget).val()

    var lowerCount = 0;
    var upperCount = 0;
    var numberCount = 0;
    var punctCount = 0;

    for(var i=0, len=newValue.length; i<len; i++){
      ch = newValue.charAt(i);
      
      if(ch >= 'A' && ch <= 'Z'){
        ++upperCount;
      } else if(ch >= 'a' && ch <= 'z') {
        ++lowerCount;
      } else if(ch >= '0' && ch <= '9') {
        ++numberCount;
      } else {
        ++punctCount;
      }
    }

    if(lowerCount > 0){
      $('#pwd-lower').attr('class', 'valid');
    } else {
      $('#pwd-lower').attr('class', 'invalid');
    }

    if(upperCount > 0){
      $('#pwd-upper').attr('class', 'valid');
    } else {
      $('#pwd-upper').attr('class', 'invalid');
    }

    if(numberCount > 0){
      $('#pwd-number').attr('class', 'valid');
    } else {
      $('#pwd-number').attr('class', 'invalid');
    }

    if(punctCount > 0){
      $('#pwd-punct').attr('class', 'valid');
    } else {
      $('#pwd-punct').attr('class', 'invalid');
    }

    if(newValue.length >= 10){
      $('#pwd-length').attr('class', 'valid');
    } else {
      $('#pwd-length').attr('class', 'invalid');
    }

    var pwdClass = (lowerCount > 0 ? 1 : 0) + (upperCount > 0 ? 1 : 0) + (punctCount > 0 ? 1 : 0) + (numberCount > 0 ? 1 : 0);

    if(pwdClass >= 3){
      $('#pwd-class').attr('class', 'valid');
    } else {
      $('#pwd-class').attr('class', 'invalid');
    }

  });
}