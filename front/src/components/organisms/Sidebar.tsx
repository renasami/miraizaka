import React from 'react';
import SidebarItem from '../molecules/SidebarItem'
import List from "@material-ui/core/List";
import HomeIcon from "@material-ui/icons/Home";
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import AccountBoxIcon from '@mui/icons-material/AccountBox';

type Props {

}
const SideBar:React.FC<Props> = (props:Props) => {
    const listProps = [
        {
            "className":"",
            "icon":<HomeIcon />,
            "itemText":"",
            "to":"",
            "onClick":""
        }
    ]
    return (
        <>
            <List>
            </List>
        </>
    )
}

export default SideBar;