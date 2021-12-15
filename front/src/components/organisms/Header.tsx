import React from 'react';
import clsx from "clsx";
import CssBaseline from "@material-ui/core/CssBaseline";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import { ClassNameMap } from '@mui/material/styles';
import IconButton from "@material-ui/core/IconButton";
import MenuIcon from "@material-ui/icons/Menu";
import Typography from "@material-ui/core/Typography";

type Props = {
    classes:ClassNameMap
    open:boolean
    setOpen:React.Dispatch<React.SetStateAction<boolean>>
}

//TODO:もう少し細い切り分け（sidebarに則った)
const Header: React.FC<Props> = (props: Props) => {

    const handleDrawerOpen = () => {
        props.setOpen(true);
    }

    return ( 
        <>
        <CssBaseline/>
        <AppBar
          position="absolute"
          className={clsx(props.classes.appBar, props.open && props.classes.appBarShift)}
        >
            <Toolbar className={props.classes.toolbar}>
            <IconButton
              edge="start"
              color="inherit"
              aria-label="open drawer"
              onClick={handleDrawerOpen}
              className={clsx(
                props.classes.menuButton,
                props.open && props.classes.menuButtonHidden
              )}
            >
              <MenuIcon />
            </IconButton>
            <Typography
              component="h1"
              variant="h6"
              color="inherit"
              noWrap
              className={props.classes.title}
            >
              MyjLab 入退室管理
            </Typography>
          </Toolbar>
        </AppBar>
        </>
    )
}

export default Header