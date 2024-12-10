// Import Firebase functions
import { initializeApp } from "firebase/app";
import { getMessaging, getToken, onMessage } from "firebase/messaging";

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyD6hwSdqMnt-E6zcPtmoLh5Fl-WSflFbEQ",
  authDomain: "fir-chat-188b9.firebaseapp.com",
  projectId: "fir-chat-188b9",
  storageBucket: "fir-chat-188b9.firebasestorage.app",
  messagingSenderId: "172801949831",
  appId: "1:172801949831:web:e8acfa343680bd4a10f822",
  measurementId: "G-HKRC54M3K4"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const messaging = getMessaging(app);


const vapidKey = "BE1psWMabVnS9C-p_Difji4fYkpWbJhHc0fH1-6DyBHv08QOwN2PuoNxc6YUS7_7WSe75LIONWcht8ELJfCZoRc";
export const requestFCMToken = async ()=>{
    return Notification.requestPermission()
    .then((permission)=>{
        if(permission == "granted"){
            return getToken(messaging, {vapidKey})
        }else{
            throw new Error("Notification Not Granted")
        }
    })
    .catch((err)=>{
        console.error("Error getting FCM token: ",err)
        throw err;
    })
}


export const onMessageListener = () =>
  new Promise((resolve, reject) => {
    onMessage(messaging, (payload) => {
      resolve(payload);
    });
  });
