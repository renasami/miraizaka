/* eslint-disable  */
import React from "react";
import GenericTemplate from "../templates/GenericTemplate";
import { makeStyles } from "@material-ui/core/styles";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableCell from "@material-ui/core/TableCell";
import TableContainer from "@material-ui/core/TableContainer";
import TableHead from "@material-ui/core/TableHead";
import TableRow from "@material-ui/core/TableRow";
import Paper from "@material-ui/core/Paper";

const createData = (
  name: string,
  grade: string,
  time: number,
) => {
  return { name, grade, time };
};
/*
need json
{
  id:int,
  grade:"str",(b3,b4,m1,m2,d1,d2,d3,教授)
  enterdTime:"timestamp" , (今日の入室時間で一番早い時間)
  interbal: "int" (途中退室中の時間)
}
*/

const rows = [
  createData("阿左見", "B3", 300),
  createData("sei",  "B3", 350),
  createData("小関","B3", 500),
  createData("宮治","教授",100)
];

const useStyles = makeStyles({
  table: {
    minWidth: 650,
  },
});

const ProductPage: React.FC = () => {
  const classes = useStyles();

  return (
    <GenericTemplate title="今居るメンバー">
      <TableContainer component={Paper}>
        <Table className={classes.table} aria-label="simple table">
          <TableHead>
            <TableRow>
              <TableCell>名前</TableCell>
              <TableCell align="right">学年</TableCell>
              <TableCell align="right">時間(分)</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row) => (
              <TableRow key={row.name}>
                <TableCell component="th" scope="row">
                  {row.name}
                </TableCell>
                <TableCell align="right">{row.grade}</TableCell>
                <TableCell align="right">{row.time}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </GenericTemplate>
  );
};

export default ProductPage;