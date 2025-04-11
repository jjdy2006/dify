package com.liuqn.mcp.controller;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api")
public class TextController {

    @PostMapping("/lowercase")
    public Map<String, String> convertToLowercase(@RequestBody Map<String, String> request) {
        String text = request.get("text");

        return Map.of("result", text != null ? text.toLowerCase() : "");
    }


}