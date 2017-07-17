<?php
require_once("dbconn.php");


function get_exp_for_next_level($level) {
    $exp_per_level = get_collection_data('gamerules');
    foreach ($exp_per_level as $level_range => $exp_formula){
        if (in_array($level, explode(',',$level_range))) {
            return intval(eval("return ".str_replace("oldLevel", $level, $exp_formula).';'));
        }
    }
    return -1;
}
?>
