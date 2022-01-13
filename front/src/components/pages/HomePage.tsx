import React, { useEffect, useState } from "react";
import GenericTemplate from "../templates/GenericTemplate";
import {Bar} from 'react-chartjs-2'

const data ={
    labels: ["阿左見","大倉","太田","工藤","栗原","sei","前畑","溝口","宮田","山口","物部"],

    //need json to data structure
    /* 
      {
        name:"str",
        time:"int"(all amount of a month)
      }
    */
    datasets: [
        {
            label: "今月の滞在時間",
            backgroundColor: "#008080",
            borderColor: "rgba(54, 162, 235, 0.2)",
            pointBorderWidth: 10,
            data: [...Array(12)].map(_ => Math.random() *100)

        }
    ]
}



const HomePage: React.FC = () => {
  // const [state,setState] = useState();
  // const url = "http://localhost:8080/get-now-member"
  // useEffect(()=>{
  //   fetch(url).then(resp => resp.json())
  //             .then(json => console.log(json))
  // })
  return (
    <GenericTemplate title="トップページ">
      <div>
          <h2>滞在時間</h2>
          <div>
              <Bar data={data}/>
          </div>
      </div>
    </GenericTemplate>
  );
};

export default HomePage;