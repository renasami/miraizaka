import firebase from 'firebase/auth';

export type User = firebase.User

export type AuthContextProps = {
    currentUser: User | null | undefined;
    isLoggedIn: boolean;
  };
  