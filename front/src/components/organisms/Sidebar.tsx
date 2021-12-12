import React, { useState } from 'react';
import clsx from "clsx";
import SidebarItem from '../molecules/SidebarItem'
import List from "@material-ui/core/List";
import HomeIcon from "@material-ui/icons/Home";
import MeetingRoomIcon from '@mui/icons-material/MeetingRoom';
import PeopleIcon from '@mui/icons-material/People';
import LogoutIcon from '@mui/icons-material/Logout';
import { useHistory } from 'react-router-dom';
import { signout } from '../../functions/signout';
import { ClassNameMap } from '@mui/material';
import Drawer from '@material-ui/core/Drawer';
type Props ={
    classes:ClassNameMap
}
const SideBar:React.FC<Props> = (props:Props) => {
    const history = useHistory();
    const [open,setOpen] = useState(true);
    const handleDrawerOpen = () => {
        setOpen(true);
      };
      const handleDrawerClose = () => {
        setOpen(false);
      };


    const toSignout = () => {
        signout().then((isSuccess) => {
        if (!isSuccess) return;
        history.push("/login")
        })
    }
    
    const listProps = [
        {
            "icon":<HomeIcon />,
            "itemText":"トップ",
            "to":"/",
        },
        {
            "icon":<MeetingRoomIcon />,
            "itemText":"今いるメンバー",
            "to":"/products",            
        },
        {
            "icon":<PeopleIcon />,
            "itemText":"全員",
            "to":"/all"
        },
        {
            "icon":<LogoutIcon />,
            "itemText":"ログアウト",
            "to":"/",
            "onClick":()=>toSignout(),
        },
    ]  
    return (
        <Drawer
            variant="permanent"
            classes={{
                paper: clsx(props.classes.drawerPaper, !open && props.classes.drawerPaperClose),
              }}
            open={open}
        >
            <List>
               {listProps.map(item => <SidebarItem
                    className={props.classes.link}
                    onClick={item?.onClick}
                    icon={item.icon}
                    itemText={item.itemText}
                    to={item.to}
                />)}
            </List>
        </Drawer>
    )
}

export default SideBar;

