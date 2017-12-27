<?php


function get_award_details($award_id) {
    $award_data = json_decode(file_get_contents('../awards/awards.json'), True);
    $award_data = $award_data['awards'];
    $award_details = $award_data[$award_id];
    if (!isset($award_details['message'])) {
        $award_details['message'] = '???';
    }
    return $award_details;
    
}
?>
