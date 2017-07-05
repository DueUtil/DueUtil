<?php
/**
 * Core functionality for templates
 * 
 * A very simple template solution
 * All it does it take a file & and an array (more like a dict)
 * of values to substitute in the template.
 * 
 * The values to substitute can also be other templates or arrays of
 * templates allowing for more complex pages.
 * 
 * Example Usage:
 * If the template was:
 * ----template.tpl----
 * <h1>[@name]</h1>
 * --------------------
 * 
 * Then using the key 'name' with the template & and value e.g. 'bob'
 * would output
 * <h1>bob</h1>
 * 
 * @author Ben Maxwell
 * 
 */
abstract class Template
{
    private $template_file_path;
    private $values_to_substitute;
    
    /**
     * General constructor of a template
     * 
     * @param string $template_file_path The path to the .tpl file
     * @paran object[] $values_array An associative array of substitutions (optional)
     * 
     * @author Ben Maxwell
     */
    public function __construct($template_file_path, $values_array = null)
    {
        $this->template_file_path = $template_file_path;
        if ($values_array != null)
            $this->values_to_substitute = $values_array;
        else
            $this->values_to_substitute = array();
    }
    
    /**
     * Maps a key e.g. [@example] to a value to replace it with
     * 
     * @param string $key The key in the .tpl file (just the name e.g. 'example')
     * @param object $value A a string or another template to replace that key with
     * 
     * @author Ben Maxwell
     */
    public function set_value($key, $value)
    {
        $this->values_to_substitute[$key] = $value;
    }
    
    /**
     * Sets the entire Map of keys to values to the given associative array
     * 
     * @param object[] An array of substitutions with values that are strings or templates
     * 
     * @author Ben Maxwell
     */
    public function set_values($values_array)
    {
        $this->values_to_substitute = $values_array;
    }
    
    /**
     * Gets the contents of the .tpl template file if it exists
     * 
     * @return string The file contents
     * 
     * @author Ben Maxwell
     */
    protected function template_contents()
    {
        if (!file_exists($this->template_file_path))
            return null;
        return file_get_contents($this->template_file_path,FILE_SKIP_EMPTY_LINES);
    }
    
    /**
     * Carrys out all the substitutions (including those in child templates) and generates the html
     * 
     * @return string The the html of the template after all substitutions have been performed
     * 
     * @author Ben Maxwell
     */
    public function output()
    {
        $output = $this->template_contents();
        if ($output === null)
            return "Could not load template [$this->template_file_path]";
        // Get value & key from array 
        foreach ($this->values_to_substitute as $key => $value_to_substitute) {
            $tag_to_replace = "[@$key]";
            // replace the tag (if it exists in the template file)
            if ($value_to_substitute instanceof Template)
                $value_to_substitute = $value_to_substitute->output();
            elseif (is_array($value_to_substitute))
                $value_to_substitute = Template::merge_templates($value_to_substitute);
            
            $output = Template::replace_with_indent($tag_to_replace, $value_to_substitute, $output);
        }
        
        return $output;
    }
    
    /**
     * Outputs the template and echos the result.
     * 
     * @author Ben Maxwell
     */
    public function show()
    {
        echo $this->output();
    }
    
    /**
     * Replaces a substring in a string keeping indention if the substitute string spans more than one line
     * 
     * @param string $value The substring to be replaced
     * @param string $substitute The string for the value to be replaced with
     * @param string $string The original string
     * 
     * @return string The result of the replacement with indentation intact
     * 
     * @author Ben Maxwell
     */
    public static function replace_with_indent($value,$substitute,$string)
    {
        $string = str_replace("\t","    ",$string);
        foreach (explode("\n",$string) as $line){
          if(substr_count($string,$value)==0)
              break;
          for($value_in_line = 1;
              $value_in_line <= substr_count($line,$value);
                                        $value_in_line++){
              $pos = strpos($line,$value);
              $indentaion = str_repeat(' ',$pos);
              $replacement = explode("\n",$substitute);
              foreach (array_slice($replacement,1) as $line_num => $line)
                if (!empty(trim($line)))
                    $replacement[$line_num + 1] = $indentaion.$line;
                else
                    $replacement[$line_num + 1]  = '';
              $replacement = implode("\n",array_filter($replacement));
              $string = substr_replace($string,$replacement,strpos($string,$value),strlen($value));
          }
        }
        return $string;
    }
    //P.s. Explode & Implode are great function names.
    
    /**
     * Gets output for each template in an array of templates and returns the output as one string
     * 
     * @param Template[] $templates to merge
     * 
     * @return string The output of all the templates combined
     * 
     * @author Ben Maxwell
     */
    public static function merge_templates($templates)
    {
        $output = "";
        foreach ($templates as $template) {
            if (is_array($template))
                $output = $output . Template::merge_templates($template);
            else if (!($template instanceof Template))
                return "Somthing went wrong. One of the 'templates' was not a template.";
            else
                $output = $output . $template->output();
        }
        return $output;
    }
}
?>
