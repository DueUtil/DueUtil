<?php
require_once("../scripts/sidebar.php");
require_once("../scripts/dbconn.php");
require_once("../scripts/util.php");

/*
 * Command listing
 */

/* Sidebar start */


/* Sidebar end */

// Show dashboard.

$viewable_command_perms = array("PLAYER","DISCORD_USER","SERVER_ADMIN","REAL_SERVER_ADMIN");


$all_commands_data = get_collection_data('commands');
array_shift($all_commands_data);

$command_help = array();
$command_help[] = new StaticContent("<span class='big-p mdl-layout-title' style='font-size:18px;text-align:center'>DueUtil has a bunch of commands (with more on the way) that you can use!<br>"
                                    ."The default command prefix for DueUtil is <code>!</code> or mentioning the bot.<br>"
                                    ."The prefix the bot uses can be changed with the <code>!setcmdkey</code> command (listed in the util section).</span>");

# Sort categorys apha
ksort($all_commands_data);
foreach ($all_commands_data as $category_name => $command_category){
    $command_boxes = array();
    # Sort help context by length (asc)
    usort($command_category, "cmp");
    foreach ($command_category as $command_info){
        if ($command_info["hidden"] or !in_array($command_info["permission"],$viewable_command_perms))
            continue;
        $help = due_markdown_to_html(rtrim($command_info["help"]));
        if ($command_info["permission"] == "PLAYER" || $command_info["permission"] == "DISCORD_USER"){
            $perm_icon = "people";
            $perm_colour = "#95d3bd";
            $perm_message = "This command can be used by anyone!";
        } else if ($command_info["permission"] == "SERVER_ADMIN") {
            $perm_icon = "security";
            $perm_colour= "#ffb347";
            $perm_message = "This command is for server admins or due commanders!";
        } else {
            $perm_icon = "security";
            $perm_colour= "#ff6961";
            $perm_message = "This command is only for server admins";
        }
        $aliases_list = $command_info["aliases"];
        $aliases_count = sizeof($aliases_list);
        if ($aliases_count >= 1) {
            if ($aliases_count == 1) {
                $aliases_word = "Alias";
            } else if ($aliases_count > 1) {
                $aliases_word = "Aliases";
            }
            $aliases = implode(", ", $aliases_list);
            $help = $help."<h6 class=\"aliases\">$aliases_word:</h6> $aliases";
        }
        
        $command_boxes[] = new CommandBox($command_info["name"],$help,$perm_icon,$perm_colour,$perm_message);
    }
    $command_list = new CommandList('<i class="material-icons">keyboard_arrow_right</i>'.$category_name,$command_boxes);
    $command_help[] = $command_list;
}
(new StandardLayout($sidebar,$command_help, $title = "<h2>Commands</h2>", "DueUtil command list and help."))->show();


function cmp($command, $other_command) {
  return strlen($command["help"]) - strlen($other_command["help"]);
}
?>
