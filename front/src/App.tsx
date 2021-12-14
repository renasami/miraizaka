import React, { useEffect, useState } from "react";
import {
  HashRouter as Router,
  Redirect,
  Route,
  Switch,
} from "react-router-dom";

import ProductPage from "./components/pages/ProductPage";
import HomePage from "./components/pages/HomePage";
import Login from "./components/pages/Login";
import AllMembers from "./components/pages/AllMembers";
import LoginAdmin from "./components/pages/LoginAdmin";
import { getAuth } from "firebase/auth";
import { User } from "./type";

const App: React.FC = () => {
  const auth = getAuth();
  const [currentUser, setCurrentUser] = useState<User | null | undefined>(
    undefined
  );
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  // const location = useLocation();

  useEffect(() => {
    auth.onAuthStateChanged(async (user) => {
      if (user) {
        setCurrentUser(user);
        setIsLoggedIn(true);
      } else {
        setIsLoggedIn(false);
      }
    });
  });

  return (
    <Router>
      <Switch>
        <Route path="/products" render={_ => isLoggedIn ? (<ProductPage/>):(<Redirect to="/login"/>)} exact />
        <Route path="/" render={_ => isLoggedIn ? (<HomePage/>):(<Redirect to="/login"/>)} exact />
        <Route path="/all" render={_ => isLoggedIn ? (<AllMembers/>):(<Redirect to="/login"/>)} exact />  
        <Route path="/login" render={_ => isLoggedIn ? (<Redirect to="/"/>):(<Login/>)} exact />
        <Route path="/ytk" component={LoginAdmin} exact />
      </Switch>
    </Router>
  );
};

export default App;
