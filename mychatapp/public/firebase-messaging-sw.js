importScripts('https://www.gstatic.com/firebasejs/10.13.2/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.13.2/firebase-messaging-compat.js');

const firebaseConfig = {
    apiKey: "AIzaSyD6hwSdqMnt-E6zcPtmoLh5Fl-WSflFbEQ",
    authDomain: "fir-chat-188b9.firebaseapp.com",
    projectId: "fir-chat-188b9",
    storageBucket: "fir-chat-188b9.firebasestorage.app",
    messagingSenderId: "172801949831",
    appId: "1:172801949831:web:e8acfa343680bd4a10f822",
    measurementId: "G-HKRC54M3K4"
  };

firebase.initializeApp(firebaseConfig);
const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
    console.log("Background Message received: ", payload);
    const notificationTitle = payload.notification.title;
    const notificationOptions = {
        body: payload.notification.body,
        icon: "/firebase-logo.png",
    };

    self.registration.showNotification(notificationTitle, notificationOptions);
});
