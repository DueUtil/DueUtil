<?php
require_once("dbconn.php");

$exp_per_level = get_collection_data('gamerules');

function get_exp_for_next_level($level) {
    global $exp_per_level;
    foreach ($exp_per_level as $level_range => $exp_formula){
        if (in_array($level, explode(',',$level_range))) {
            return intval(eval("return ".str_replace("oldLevel", $level, $exp_formula).';'));
        }
    }
    return -1;
}
?>
