import { AnyMxRecord } from 'dns';
import React from 'react';
import Button from "@material-ui/core/Button";

type Props = {
    text: string,
    func?: any,
    style?:Object,
}
const BuyButton = (props: Props) => {
    return (
        <Button 
        onClick={props.func}
        variant="outlined"
        >{props.text}</Button>
    )
}

export default BuyButton;