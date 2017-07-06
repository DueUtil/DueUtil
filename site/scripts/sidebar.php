<?php
require_once("../scripts/templates.php");

$sidebar_content = array();
$sidebar_content[] = new User(array('name' => 'Placeholder',
                                    'id' => 'Placeholder',
                                    'avatar' => 'https://discordapp.com/assets/dd4dbc0016779df1378e7812eabaa04d.png'));
$sidebar_content[] = new Navigation('General',
                                    array(
                                      'DueUtil' => '../home',
                                      'How To Guide'=>'#',
                                      'Commands'=>'../commands',
                                      'Leaderboard'=>'../leaderboard'
                                    ));                                  
$sidebar_content[] = new Navigation('Tools',
                                    array(
                                      'Quest Builder'=>'#',
                                      'Weapon Builder'=>'#',
                                      'MyDashboard' => '#'
                                    ));
$sidebar = new Sidebar($sidebar_content);
?>
