// Firebase Config
const firebaseConfig = {
  apiKey: "AIzaSyD6kjLR_ppge8lnrK155wJRuzFiiC9hois",
  authDomain: "ddcet-otp.firebaseapp.com",
  projectId: "ddcet-otp",
  storageBucket: "ddcet-otp.firebasestorage.app",
  messagingSenderId: "534713346199",
  appId: "1:534713346199:web:a00d0032380a58692821d2"
};

firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();

// Recaptcha
window.recaptchaVerifier = new firebase.auth.RecaptchaVerifier(
  "recaptcha-container",
  {
    size: "normal"
  }
);

let confirmationResult;

const sendOtpBtn = document.getElementById("sendOtpBtn");
const verifyOtpBtn = document.getElementById("verifyOtpBtn");
const otpSection = document.getElementById("otpSection");
const registerBtn = document.getElementById("registerBtn");

sendOtpBtn.addEventListener("click", function () {

  const mobile = document.getElementById("mobile").value;

  if (!/^[6-9][0-9]{9}$/.test(mobile)) {
    alert("Enter valid Indian mobile number.");
    return;
  }

  const phoneNumber = "+91" + mobile;

  auth.signInWithPhoneNumber(phoneNumber, window.recaptchaVerifier)
    .then(function (result) {
      confirmationResult = result;

      // 👇 OTP BOX SHOW KARO
      otpSection.style.display = "block";

      alert("OTP Sent Successfully!");
    })
    .catch(function (error) {
      alert(error.message);
    });

});

verifyOtpBtn.addEventListener("click", function () {

  const otp = document.getElementById("otp").value;

  confirmationResult.confirm(otp)
    .then(function () {
      alert("Mobile Verified Successfully!");
      registerBtn.disabled = false;
    })
    .catch(function () {
      alert("Invalid OTP");
    });

});