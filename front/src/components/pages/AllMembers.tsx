import React from "react";
import GenericTemplate from "../templates/GenericTemplate";
const AllMembers:React.FC = () => {
    const members = ["阿左見","大倉","太田","工藤","栗原","sei","前畑","溝口","宮田","山口","物部"]
    //ゆるぼ：スタイル

    return (
      <>
        <GenericTemplate title="all members">
          <h1>All Members</h1>
          <ul>
              {members.map(member => <li>{member}</li>)}
          </ul>
        </GenericTemplate>
      </>
    );
}

export default AllMembers