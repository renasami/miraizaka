import React from "react";
import { ClassNameMap } from '@mui/material';
import ChevronLeftIcon from "@material-ui/icons/ChevronLeft";
import IconButton from "@material-ui/core/IconButton";

type Props = {
    classes:ClassNameMap;
    setOpen: React.Dispatch<React.SetStateAction<boolean>>
}


const SidebarIcon: React.FC<Props> = (props: Props) => {
    const handleDrawerClose = () => {
        props.setOpen(false);
    }

    return (
        <div className={props.classes.toolbarIcon}>
            <IconButton onClick={handleDrawerClose}>
              <ChevronLeftIcon />
            </IconButton>
        </div>
    )
}

export default SidebarIcon