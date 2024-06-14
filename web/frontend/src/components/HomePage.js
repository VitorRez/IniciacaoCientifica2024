import React, { Component } from 'react';
import AccessPage from './AccessPage';
import VoterPage from './VoterPage';
import { BrowserRouter as Router, Routes, Route, Link, Redirect } from "react-router-dom";

export default class HomePage extends Component {
    constructor(props) {
        super(props);

    }

    render() {
        return <Router>
            <Routes>
                <Route exact path='/' element={<p>This is the home page</p>} ></Route>
                <Route path='/access' element={<AccessPage></AccessPage>}></Route>
                <Route path='/voterpage' element={<VoterPage></VoterPage>}></Route>
            </Routes>
        </Router>;
    }
}