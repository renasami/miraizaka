import { getAuth, signOut } from "firebase/auth";


export const signout = ():Promise<boolean> => {
    const auth = getAuth();
    
    const results =  signOut(auth).then(() => {
        // Sign-out successful.
        console.log("Sign-out successful")
        return true
      }).catch((error) => {
        // An error happened.
        alert(error.message)
        return false
    });
    return results
}