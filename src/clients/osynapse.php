<?php
/**
    OpenSynapse PHP5 Client, Umut Aydin(MrGoodbyte), Copyright (c) 2011
    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
    to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
    sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
    FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
    WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/

class OpenSynapse
{
    private $hostname,
            $port,
            $socket;


    public function __construct($host, $port)
    {
        $this->hostname = $host;
        $this->port = $port;
    }

    public function connect()
    {
        if ($this->isConnected())
            return true;

        try 
        {
            $this->socket = fsockopen($this->hostname, $this->port);
            if ($this->isConnected())
                return true;

            return true;
        }
        catch (Exception $e) { return false; }
    }

    public function close()
    {
        try { fclose($this->socket); }
        catch (Exception $e) { }
    }

    public function send($task, $parameters)
    {
        if (!$this->isConnected())
            if (!$this->connect())
                return false;

        try
        {
            fwrite($this->socket, json_encode(array(
                'c' => 'cll',
                'p' => array(
                    'n' => $task,
                    'd' => $parameters
                )
            )));
            return $this->response(fgets($this->socket));
        }
        catch (Exception $e) { return false; }
    }

    private function response($response)
    {
        try
        {
            $js = json_decode($response);
            if (is_array($js) && isset($js['e']) && ($js['e'] == 0))
                return $js['r'];

            return false;
        }
        catch (Exception $e) { return false; }
    }

    private function isConnected()
    {
        if (!$this->socket)
            return false;

        return true;
    }
}
?>