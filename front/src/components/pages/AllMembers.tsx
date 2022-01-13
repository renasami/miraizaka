import React, { useEffect, useState } from "react";
import GenericTemplate from "../templates/GenericTemplate";

type AllMember = {
  id: number
  display_name: string
  name: string
  graduated_year?: string
  grade: string
}

type MemberDisplay = {
  display: string
  grade: string
}

const AllMembers:React.FC = () => {
    // const members = ["阿左見","大倉","太田","工藤","栗原","sei","前畑","溝口","宮田","山口","物部"]
    //ゆるぼ：スタイル
    const [state,setState] = useState<MemberDisplay[]>([]);
    const url = 'http://10.0.0.64:8080/get-all-ungraduated-member'
    useEffect(() => {
      fetch(url).then(resp => resp.json())
      .then(json => {
          const members = json.map((data:AllMember) =>  {return {display:data.display_name,grade:data.grade}})
          setState([...members])
      })
    },[])
    return (
      <>
        <GenericTemplate title="all members">
          <h1>All Members</h1>
          <h3>院生</h3>
          <ul>
           { state.filter((member) => member.grade.includes("M")).map((dis,key) => <li key={key}>{dis.display}</li>)}
          </ul>
          <h3>4年生</h3>
          <ul>
           { state.filter((member) => member.grade === "B4").map((dis,key) => <li key={key}>{dis.display}</li>)}
          </ul>
          <h3>3年生</h3>
          <ul>
           { state.filter((member) => member.grade === "B3").map((dis,key) => <li key={key}>{dis.display}</li>)}
          </ul>
        </GenericTemplate>
      </>
    );
}

export default AllMembers