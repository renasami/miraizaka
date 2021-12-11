import {getAuth} from 'firebase/auth'

const auth = getAuth();

let status:boolean 
export const isLogin = ():boolean => {
    auth.onAuthStateChanged(function(user) {
        if (user) status =  true;
        else status = false;
    });
    return status
}