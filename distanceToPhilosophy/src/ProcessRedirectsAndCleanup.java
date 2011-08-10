import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Queue;
import java.util.Set;

public class ProcessRedirectsAndCleanup {
  
  private TokenDictionary tokenDictionary = new TokenDictionary();
  
  private final String redirectsFile, edgesFile;
  
  List<Integer> rawEdges = new LinkedList<Integer>();
  Set<Integer> validNodes = new HashSet<Integer>();
  Map<Integer,Integer> redirects = new HashMap<Integer,Integer>();  
  
  private Map<Integer,List<Integer>> edges = new HashMap<Integer,List<Integer>>();
  
  public static void main(String args[]) throws IOException {
  	if (args.length != 2) {
  		throw new RuntimeException("ProcessRedirectsAndCleanup <redirectsFile> <rawEdgesFile>");
  	}	
    new ProcessRedirectsAndCleanup(args).go();
  }
  
  public ProcessRedirectsAndCleanup(String[] args) {    
    this.redirectsFile = args[0];
    this.edgesFile = args[1];   
  }
  
  public void go() throws IOException {
    readRawEdgesAndValidNodes();    
    readRedirectsFile();
    processRawEdgesUsingRedirects();
  }

  private void readRawEdgesAndValidNodes() throws FileNotFoundException, IOException { 
    
    BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(edgesFile)));    
    
    // first read from file and just convert to idx    
    int linesProcessed=0;        
    String next;    
    while((next=reader.readLine())!=null) {

      if (++linesProcessed%100000==0) {
        System.err.println("parseEdgesFile:"+
            " linesProcessed="+linesProcessed+
            " rawEdges.size()="+rawEdges.size()+
            " idxToToken.size="+tokenDictionary.idxToToken.size());
      }

      String[] cols = next.split("\t");
      if (cols.length!=2) {
        System.err.println("parseEdgesFile: strange input that doesnt split on tab... ["+next+"]");
        continue;
      }
            
      int fromNode = tokenDictionary.idxForToken(cols[0]);
      int toNode = tokenDictionary.idxForToken(captialise(cols[1])); // often toNode needs capitalisation to match fromNode or redirects
            
      validNodes.add(fromNode);
      rawEdges.add(fromNode);
      rawEdges.add(toNode);
      
    }

    System.err.println("parseEdgesFile:"+
        " linesProcessed="+linesProcessed+
        " rawEdges.size()="+rawEdges.size()+
        " idxToToken.size="+tokenDictionary.idxToToken.size());
    
    reader.close();           
  }  
  
  private void readRedirectsFile() throws IOException {  
    BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(redirectsFile)));
    
    int numIgnoredSlashN=0, numNotIgnored=0;
    int numDuplicateRedirects=0, numContradictoryRedirects=0;
    int numInvalidFrom=0, numInvalidTo=0;
    int total = 0;
    String next;
    while((next=reader.readLine())!=null) {
      
      if (++total%100000==0) {
        System.err.println("parseRedirectsFile: total="+total+
            " numIgn\\N="+numIgnoredSlashN+
            " numNotIgn\\N="+numNotIgnored+
            " numDupRed="+numDuplicateRedirects+
            " numConrRed="+numContradictoryRedirects+
            " idxToToken.size="+tokenDictionary.idxToToken.size());
      }
      
      String[] cols = next.split("\t");      
      
      if (cols[2].equals("\\N")) {
        numIgnoredSlashN++;
        continue;
      }

      int fromNode = tokenDictionary.idxForToken(cols[1]);
      int toNode = tokenDictionary.idxForToken(cols[2]);                 
      
      // breaks toNode -> capitalisation -> redirect case ??
//      if (!validNodes.contains(fromNode)) {
//        numInvalidFrom++;
//        continue;
//      }
//      if (!validNodes.contains(toNode)) {
//        numInvalidTo++;
//        continue;
//      }
      
      if (redirects.containsKey(fromNode)) {
        if (redirects.get(fromNode) == toNode) {
          numDuplicateRedirects++;
        }
        else {
          numContradictoryRedirects++;
          // and allow new one to clobber old one
        }
      }
            
      redirects.put(fromNode, toNode);
      numNotIgnored++;           
      
    }

    System.err.println("parseRedirectsFile: total="+total+
        " numIgn\\N="+numIgnoredSlashN+
        " numNotIgn\\N="+numNotIgnored+
        " numDupRed="+numDuplicateRedirects+
        " numConrRed="+numContradictoryRedirects+
        " idxToToken.size="+tokenDictionary.idxToToken.size());
    
    reader.close();    
  }  
      
  private void processRawEdgesUsingRedirects() { 

    int numRedirects=0, numSuccessfulCamelCasings=0;
    int numCamelCasingRedirects=0, numUnsuccessfulCamelCasings=0, numExceptionsCamelCasings=0;
    int linesProcessed=0;
    
    while(rawEdges.size() > 0) {  
      
      if (++linesProcessed%100000==0) {
        System.err.println("confirming edges:"+
            " linesProcessed="+linesProcessed+
            " numRedirects="+numRedirects+
            " numCCRedirects="+numCamelCasingRedirects+
            " numSuccCC="+numSuccessfulCamelCasings+
            " numUnsuccCC="+numUnsuccessfulCamelCasings+
            " numExcepCC="+numExceptionsCamelCasings+
            " idxToToken.size="+tokenDictionary.idxToToken.size());
      }
      
      // we always trust the fromNode ...
      int fromNode = rawEdges.remove(0);
      
      // ... but we always need additional checking on the 'toNode'
      int toNode = rawEdges.remove(0);
      // redirects toNode if required
      if (redirects.containsKey(toNode)) {  
        System.err.println("parseEdgesFile: redirecting "+
            "["+tokenDictionary.idxToToken.get(toNode)+"] -> ["+tokenDictionary.idxToToken.get(redirects.get(toNode))+"]");
        toNode = redirects.get(toNode);
        numRedirects++;
      }
      // check toNode is valid
      if (!validNodes.contains(toNode)) {
        System.err.println("parseEdgesFile: warning! toNode not valid! edge "+tokenDictionary.prettyEdgeForIdxs(fromNode,toNode));
      }
      
      System.out.println(tokenDictionary.outputEdgeForIdxs(fromNode,toNode));      
            
    }

    System.err.println("confirming edges: (final) "+
        " linesProcessed="+linesProcessed+
        " numRedirects="+numRedirects+
        " numCCRedirects="+numCamelCasingRedirects+
        " numSuccCC="+numSuccessfulCamelCasings+
        " numUnsuccCC="+numUnsuccessfulCamelCasings+
        " numExcepCC="+numExceptionsCamelCasings+
        " idxToToken.size="+tokenDictionary.idxToToken.size());    
  }

  private static String captialise(String s) {    
    if (s.length()==0 || Character.isUpperCase(s.charAt(0))) {
      return s;
    }
    return s.substring(0,1).toUpperCase() + s.substring(1, s.length());    
  }
  
}

