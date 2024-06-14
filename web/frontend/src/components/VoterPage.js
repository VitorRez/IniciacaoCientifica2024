import React, { Component } from "react";
import Button from "@material-ui/core/Button";
import Grid from "@material-ui/core/Grid";
import Typography from "@material-ui/core/Typography";
import TextField from "@material-ui/core/TextField";
import FormHelperText from "@material-ui/core/FormHelperText";
import FormControl from "@material-ui/core/FormControl";
import { Form, Link } from "react-router-dom";
import Radio from "@material-ui/core/Radio";
import RadioGroup from "@material-ui/core/RadioGroup";
import FormControlLabel from "@material-ui/core/FormControlLabel";

export default class VoterPage extends Component{
    constructor(props){
        super(props);
        this.state = {
            password: "",
            office: "",
            officeid: "",
        };
    }

    render() {
        return(
            <Grid container spacing={1}>
                <Typography component="h2" variant="h2">{this.state.name}</Typography> 
            </Grid>
        );
    }

}