import React from "react";
import ListItem from "@material-ui/core/ListItem";
import ListItemIcon from "@material-ui/core/ListItemIcon";
import ListItemText from "@material-ui/core/ListItemText";
import { Link } from "react-router-dom";
type Props = {
  onClick?: () => void;
  className: string;
  itemText: string;
  icon: JSX.Element;
  to: string;
};

const SidebarItem: React.FC<Props> = (props: Props) => {
  return (
    <>
      <Link to={props.to} className={props.className}>
        <ListItem button onClick={props.onClick}>
          <ListItemIcon>{props.icon}</ListItemIcon>
          <ListItemText primary={props.itemText} />
        </ListItem>
      </Link>
    </>
  );
};

export default SidebarItem;
